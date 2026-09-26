package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service
public class PromptGeneratorService {

    public String generatePromptForTopic(String topic) {
        if (topic == null || topic.trim().isEmpty()) {
            return "### 🎯 OMEGA Prompt Generator\n\nPlease specify a topic or goal for the prompt (e.g., *\"give me a prompt for a React login page\"* or *\"give me a prompt to write a resume\"*).";
        }

        String cleanTopic = topic.trim();
        String lower = cleanTopic.toLowerCase();

        String role;
        String constraints;
        String outputFormat;

        if (lower.contains("react") || lower.contains("code") || lower.contains("html") || lower.contains("css") || lower.contains("java") || lower.contains("python") || lower.contains("app") || lower.contains("web") || lower.contains("script")) {
            role = "Senior Full-Stack Software Engineer & Technical Architect";
            constraints = "- Ensure clean, modular, production-ready code with comprehensive inline documentation.\n" +
                          "- Include state validation, error handling, edge cases, and modern UI/UX principles.\n" +
                          "- Follow clean architecture, DRY design patterns, and framework conventions.";
            outputFormat = "1. Technical Approach & Architecture Overview\n" +
                           "2. Complete, Copyable Code Files with Language Annotations\n" +
                           "3. Integration & Setup Instructions\n" +
                           "4. Time & Space Complexity Analysis";
        } else if (lower.contains("resume") || lower.contains("job") || lower.contains("interview") || lower.contains("career") || lower.contains("cover letter") || lower.contains("cv")) {
            role = "Executive Career Strategist and Professional Resume Writer";
            constraints = "- Focus on quantifiable impact metrics (e.g., increased revenue by 25%, reduced latency by 40%).\n" +
                          "- Format for ATS (Applicant Tracking System) optimization using standard headers.\n" +
                          "- Utilize strong action verbs and professional, compelling executive phrasing.";
            outputFormat = "1. Professional Summary / Executive Elevator Pitch\n" +
                           "2. Key Core Competencies & Skills List\n" +
                           "3. Experience Achievements formatted as Action + Context + Quantified Impact\n" +
                           "4. Education & Credentials Section";
        } else if (lower.contains("email") || lower.contains("marketing") || lower.contains("copy") || lower.contains("ad") || lower.contains("sales") || lower.contains("newsletter")) {
            role = "Master Direct-Response Copywriter & Conversion Specialist";
            constraints = "- Craft high-open-rate subject lines with strong curiosity or value hooks.\n" +
                          "- Utilize persuasive storytelling, clear value propositions, and a single focused Call to Action (CTA).\n" +
                          "- Maintain an engaging, reader-centric, and professional tone.";
            outputFormat = "1. 3 High-Converting Subject Line Options\n" +
                           "2. Hook & Personal Intro\n" +
                           "3. Value Proposition & Solution Bullet Points\n" +
                           "4. Clear Call to Action (CTA) & Sign-off";
        } else {
            role = "Domain Expert & Strategic AI Consultant";
            constraints = "- Provide a clear, thoroughly researched, and actionable response.\n" +
                          "- Address potential edge cases, best practices, and key considerations.\n" +
                          "- Ensure maximum clarity, structure, and depth.";
            outputFormat = "1. Executive Summary & Core Objective\n" +
                           "2. Step-by-step Detailed Implementation Framework\n" +
                           "3. Best Practices & Key Considerations\n" +
                           "4. Actionable Next Steps";
        }

        StringBuilder sb = new StringBuilder();
        sb.append("### 🎯 OMEGA Prompt Generator (Detected Intent: Prompt Generation)\n\n");
        sb.append("**Target Goal / Topic**: *\"").append(cleanTopic).append("\"*\n\n");
        sb.append("#### 📄 Generated Ready-to-Use Prompt\n");
        sb.append("```markdown\n");
        sb.append("# Role & Persona\n");
        sb.append("Act as a ").append(role).append(". Your task is to generate a comprehensive solution for: \"").append(cleanTopic).append("\".\n\n");

        sb.append("# Primary Objective\n");
        sb.append("Create a top-tier, highly detailed, and production-ready output covering: ").append(cleanTopic).append(".\n\n");

        sb.append("# Constraints & Standards\n");
        sb.append(constraints).append("\n\n");

        sb.append("# Context & Guidelines\n");
        sb.append("- Tone: Professional, structured, clear, and actionable.\n");
        sb.append("- Scope: Comprehensive and thorough, leaving no critical steps or edge cases unaddressed.\n\n");

        sb.append("# Expected Output Format\n");
        sb.append(outputFormat).append("\n");
        sb.append("```\n\n");

        sb.append("💡 **Usage Tip**: Copy the generated prompt inside the block above and paste it directly into any AI assistant (or send it right here in OMEGA) to execute the task!");

        return sb.toString();
    }
}
