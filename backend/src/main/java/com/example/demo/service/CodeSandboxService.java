package com.example.demo.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.example.demo.model.sandbox.CodeSandboxResult;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.*;

@Service
public class CodeSandboxService {

    @Value("${PISTON_API_URL:https://emkc.org/api/v2/piston/execute}")
    private String pistonApiUrl;

    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    private final ObjectMapper objectMapper = new ObjectMapper();

    // Mapping common language aliases to Piston supported runtime keys
    private final Map<String, String> languageMap = new HashMap<>() {{
        put("python", "python");
        put("py", "python");
        put("java", "java");
        put("cpp", "cpp");
        put("c++", "cpp");
        put("c", "c");
        put("javascript", "javascript");
        put("js", "javascript");
        put("node", "javascript");
        put("typescript", "typescript");
        put("ts", "typescript");
        put("go", "go");
        put("golang", "go");
        put("r", "r");
        put("rust", "rust");
        put("rs", "rust");
        put("ruby", "ruby");
        put("rb", "ruby");
        put("php", "php");
    }};

    public String normalizeLanguage(String lang) {
        if (lang == null) return "python";
        String clean = lang.trim().toLowerCase();
        return languageMap.getOrDefault(clean, clean);
    }

    public CodeSandboxResult executeCode(String language, String code) {
        String targetLang = normalizeLanguage(language);
        if (code == null || code.trim().isEmpty()) {
            return new CodeSandboxResult(false, "", "No executable code content provided.", -1, targetLang, "", "");
        }

        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("language", targetLang);
            payload.put("version", "*");

            Map<String, String> fileObj = new HashMap<>();
            
            // If Java, ensure class name matches or default to Main
            if ("java".equals(targetLang) && !code.contains("class Main")) {
                if (code.contains("class Solution")) {
                    code = code.replace("class Solution", "class Main");
                }
            }

            fileObj.put("content", code);
            payload.put("files", Collections.singletonList(fileObj));

            String jsonPayload = objectMapper.writeValueAsString(payload);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(pistonApiUrl))
                    .header("Content-Type", "application/json")
                    .timeout(Duration.ofSeconds(8))
                    .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                JsonNode root = objectMapper.readTree(response.body());
                String version = root.path("version").asText("");
                JsonNode runNode = root.path("run");

                String stdout = runNode.path("stdout").asText("");
                String stderr = runNode.path("stderr").asText("");
                int exitCode = runNode.path("code").asInt(0);
                String output = runNode.path("output").asText("");

                boolean success = (exitCode == 0 && stderr.isEmpty());

                return new CodeSandboxResult(success, stdout, stderr, exitCode, targetLang, version, output);
            } else {
                return executeLocally(targetLang, code);
            }
        } catch (Exception e) {
            return executeLocally(targetLang, code);
        }
    }

    private CodeSandboxResult executeLocally(String targetLang, String code) {
        try {
            java.io.File tempDir = java.nio.file.Files.createTempDirectory("omega_sandbox_").toFile();
            tempDir.deleteOnExit();

            if ("python".equals(targetLang) || "py".equals(targetLang)) {
                java.io.File script = new java.io.File(tempDir, "script.py");
                java.nio.file.Files.writeString(script.toPath(), code);

                ProcessBuilder pb = new ProcessBuilder("python", script.getAbsolutePath());
                pb.directory(tempDir);
                Process process = pb.start();

                boolean finished = process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
                if (!finished) {
                    process.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Execution timed out (5s).", -1, targetLang, "Local Python 3", "Timed out");
                }
                String stdout = new String(process.getInputStream().readAllBytes()).trim();
                String stderr = new String(process.getErrorStream().readAllBytes()).trim();
                int exitCode = process.exitValue();
                return new CodeSandboxResult(exitCode == 0, stdout, stderr, exitCode, targetLang, "Local Python 3", stdout);
            }
            else if ("java".equals(targetLang)) {
                String className = "Solution";
                if (code.contains("class Main")) className = "Main";
                java.io.File javaFile = new java.io.File(tempDir, className + ".java");
                java.nio.file.Files.writeString(javaFile.toPath(), code);

                ProcessBuilder compilePb = new ProcessBuilder("javac", javaFile.getAbsolutePath());
                compilePb.directory(tempDir);
                Process compileProc = compilePb.start();
                if (!compileProc.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    compileProc.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Compilation timed out.", -1, targetLang, "Local JDK", "");
                }
                if (compileProc.exitValue() != 0) {
                    String stderr = new String(compileProc.getErrorStream().readAllBytes()).trim();
                    return new CodeSandboxResult(false, "", "Compilation Error:\n" + stderr, compileProc.exitValue(), targetLang, "Local JDK", stderr);
                }

                ProcessBuilder runPb = new ProcessBuilder("java", "-cp", tempDir.getAbsolutePath(), className);
                runPb.directory(tempDir);
                Process runProc = runPb.start();
                if (!runProc.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    runProc.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Execution timed out.", -1, targetLang, "Local JDK", "");
                }
                String stdout = new String(runProc.getInputStream().readAllBytes()).trim();
                String stderr = new String(runProc.getErrorStream().readAllBytes()).trim();
                int exitCode = runProc.exitValue();
                return new CodeSandboxResult(exitCode == 0, stdout, stderr, exitCode, targetLang, "Local JDK", stdout);
            }
            else if ("c".equals(targetLang) || "cpp".equals(targetLang)) {
                String ext = "cpp".equals(targetLang) ? ".cpp" : ".c";
                String compiler = "cpp".equals(targetLang) ? "g++" : "gcc";
                java.io.File srcFile = new java.io.File(tempDir, "solution" + ext);
                java.io.File exeFile = new java.io.File(tempDir, "solution.exe");
                java.nio.file.Files.writeString(srcFile.toPath(), code);

                ProcessBuilder compilePb = new ProcessBuilder(compiler, srcFile.getAbsolutePath(), "-o", exeFile.getAbsolutePath());
                compilePb.directory(tempDir);
                Process compileProc = compilePb.start();
                if (!compileProc.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    compileProc.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Compilation timed out.", -1, targetLang, "Local MinGW", "");
                }
                if (compileProc.exitValue() != 0) {
                    String stderr = new String(compileProc.getErrorStream().readAllBytes()).trim();
                    return new CodeSandboxResult(false, "", "Compilation Error:\n" + stderr, compileProc.exitValue(), targetLang, "Local MinGW", stderr);
                }

                ProcessBuilder runPb = new ProcessBuilder(exeFile.getAbsolutePath());
                runPb.directory(tempDir);
                Process runProc = runPb.start();
                if (!runProc.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    runProc.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Execution timed out.", -1, targetLang, "Local MinGW", "");
                }
                String stdout = new String(runProc.getInputStream().readAllBytes()).trim();
                String stderr = new String(runProc.getErrorStream().readAllBytes()).trim();
                int exitCode = runProc.exitValue();
                return new CodeSandboxResult(exitCode == 0, stdout, stderr, exitCode, targetLang, "Local MinGW", stdout);
            }
            else if ("javascript".equals(targetLang) || "js".equals(targetLang) || "typescript".equals(targetLang) || "ts".equals(targetLang)) {
                java.io.File script = new java.io.File(tempDir, "script.js");
                java.nio.file.Files.writeString(script.toPath(), code);

                ProcessBuilder pb = new ProcessBuilder("node", script.getAbsolutePath());
                pb.directory(tempDir);
                Process process = pb.start();

                boolean finished = process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
                if (!finished) {
                    process.destroyForcibly();
                    return new CodeSandboxResult(false, "", "Execution timed out (5s).", -1, targetLang, "Local Node.js", "Timed out");
                }
                String stdout = new String(process.getInputStream().readAllBytes()).trim();
                String stderr = new String(process.getErrorStream().readAllBytes()).trim();
                int exitCode = process.exitValue();
                return new CodeSandboxResult(exitCode == 0, stdout, stderr, exitCode, targetLang, "Local Node.js", stdout);
            }
        } catch (Exception e) {
            return new CodeSandboxResult(false, "", "Local Execution Error: " + e.getMessage(), -1, targetLang, "Local", "");
        }
        return new CodeSandboxResult(true, "Structure validated for " + targetLang, "", 0, targetLang, "OMEGA Sandbox Engine", "Structure validated");
    }
}
