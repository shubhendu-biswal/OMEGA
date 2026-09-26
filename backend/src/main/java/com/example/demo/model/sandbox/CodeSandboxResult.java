package com.example.demo.model.sandbox;

public class CodeSandboxResult {
    private final boolean success;
    private final String stdout;
    private final String stderr;
    private final int exitCode;
    private final String language;
    private final String version;
    private final String rawOutput;

    public CodeSandboxResult(boolean success, String stdout, String stderr, int exitCode, String language, String version, String rawOutput) {
        this.success = success;
        this.stdout = stdout != null ? stdout : "";
        this.stderr = stderr != null ? stderr : "";
        this.exitCode = exitCode;
        this.language = language != null ? language : "";
        this.version = version != null ? version : "";
        this.rawOutput = rawOutput != null ? rawOutput : "";
    }

    public boolean isSuccess() {
        return success;
    }

    public String getStdout() {
        return stdout;
    }

    public String getStderr() {
        return stderr;
    }

    public int getExitCode() {
        return exitCode;
    }

    public String getLanguage() {
        return language;
    }

    public String getVersion() {
        return version;
    }

    public String getRawOutput() {
        return rawOutput;
    }
}
