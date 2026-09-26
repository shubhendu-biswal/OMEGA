package com.example.demo.intent;

import org.springframework.stereotype.Service;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class IntentDetector {

    private static class Rule {
        final IntentType type;
        final Pattern pattern;
        final List<String> responses;

        Rule(IntentType type, String regex, List<String> responses) {
            this.type = type;
            this.pattern = Pattern.compile(regex, Pattern.CASE_INSENSITIVE);
            this.responses = responses;
        }
    }

    private final List<Rule> rules = new ArrayList<>();
    private final Random random = new Random();

    // Regex for mixed greetings (e.g. "hii, can you write code for X")
    private final Pattern mixedGreetingPattern = Pattern.compile(
        "^(hi+|hy+|hye+|hello+|helo+|hlo+|hlw+|halo+|hey+|heyy+|heya+|hei+|hola+|yo+|yoo+|greetings|namaste|good\\s*(?:morning|afternoon|evening|night)|gm|gn|howdy|sup|wassup|watsup|whats\\s*up|what's\\s*up)(?:\\s+(?:there|omega|bot|friend|buddy|sir|maam|madam))?[!.,\\s]+(.*)$",
        Pattern.CASE_INSENSITIVE
    );

    // Extraction patterns for tasks, notes, and prompt generation
    private final Pattern taskCreatePattern = Pattern.compile("^(?:add\\s+task|remind\\s+me\\s+to|create\\s+task|new\\s+task|task:?)\\s+(.+)$", Pattern.CASE_INSENSITIVE);
    private final Pattern taskCompletePattern = Pattern.compile("^(?:complete|done|finish|remove|delete)\\s+task\\s+(.+)$", Pattern.CASE_INSENSITIVE);
    private final Pattern noteCreatePattern = Pattern.compile("^(?:note\\s+this\\s+down|remember\\s+this|add\\s+note|create\\s+note|save\\s+note|note:?)\\s+(.+)$", Pattern.CASE_INSENSITIVE);
    private final Pattern promptGenPattern = Pattern.compile("^(?:give\\s+me\\s+a\\s+prompt|write\\s+a\\s+prompt|create\\s+a\\s+prompt|make\\s+a\\s+prompt|generate\\s+a\\s+prompt|i\\s+need\\s+a\\s+prompt|prompt\\s+for|build\\s+a\\s+prompt)(?:\\s+(?:for|to|about))?\\s+(.+)$", Pattern.CASE_INSENSITIVE);

    public IntentDetector() {
        initDefaultRules();
    }

    public void registerIntent(IntentType type, String regex, List<String> responses) {
        rules.add(new Rule(type, regex, responses));
    }

    private void initDefaultRules() {
        // 1. Direct "Hello" Greeting -> Responds with "Hii"
        registerIntent(
            IntentType.GREETING,
            "^(hello+|helo+|halo+|hlw+|hlo+)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Hii! 😊 How are you doing today?",
                "Hii there! 👋 How can I help you today?",
                "Hii! Great to see you! What's on your mind today?",
                "Hii! 😊 Hope you're having a wonderful day!"
            )
        );

        // 2. Direct "Hi" / "Hii" / "Hey" Greeting -> Responds with "Hello"
        registerIntent(
            IntentType.GREETING,
            "^(hi+|hii+|hy+|hye+|hey+|heyy+|heya+|hei+|hola+|yo+|yoo+|howdy)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Hello! 👋 How's your day going today?",
                "Hello there! 😊 How can I assist you today?",
                "Hello! Great to connect with you. What would you like to chat about?",
                "Hello! 😊 Hope everything is going well for you today!"
            )
        );

        // 3. Time-based & Multi-lingual Indian Greetings (Odia, Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Punjabi, etc.)
        registerIntent(
            IntentType.GREETING,
            "^(good\\s*(morning|afternoon|evening|night)|gm|gn|greetings|namaste|namaskar|namaskara|namaskaram|vanakkam|kem\\s*cho|pranam|khamma\\s*ghani|sat\\s*sri\\s*akal|नमस्ते|नमस्कार|ନମସ୍କାର|নমস্কার|నమస్కారం|வணக்கம்|નમસ્તે|સત\\s*શ્રી\\s*અકાલ)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Namaste! 🙏 How can I assist you today?",
                "Greetings! 🙏 Welcome to OMEGA. How can I help you today?",
                "Hello! 👋 I am online and ready to assist you."
            )
        );

        // 4. Wellbeing questions ("how are you", "how are you brother", "how are you doing bro")
        registerIntent(
            IntentType.WELLBEING,
            "^(how\\s+(are|r)\\s+(you|u)(\\s+doing)?|how'?s\\s+it\\s+going|how\\s+do\\s+you\\s+do|how\\s+are\\s+things|how\\s+r\\s+u)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "I'm doing fantastic, thank you for asking! 😊 How are you feeling today?",
                "I'm doing awesome! How's your day going? What can I do for you?",
                "All good on my end, thank you! How are things with you today?"
            )
        );

        // 5. Positive User Mood ("i am good", "fine", "great")
        registerIntent(
            IntentType.WELLBEING,
            "^(i'?m\\s+)?(good|great|fine|awesome|wonderful|amazing|fantastic|doing\\s+well|happy|feel(?:ing)?\\s+good)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "That's wonderful to hear! 😊 What are you up to or working on today?",
                "Awesome! I'm glad you're feeling great. How can I help you today?",
                "Fantastic! Feel free to ask me anything or just chat!"
            )
        );

        // 6. Negative User Mood ("sad", "bad", "not good")
        registerIntent(
            IntentType.WELLBEING,
            "^(i'?m\\s+)?(bad|sad|not\\s+good|tired|sick|upset|feeling\\s+down|feeling\\s+low|unhappy)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Oh no, I'm really sorry to hear that. 💙 Take it easy today! Is there anything I can help with to brighten your day?",
                "Sending you good vibes! 💙 I'm here if you want to chat or need help with anything."
            )
        );

        // 7. Casual Check-ins ("what's up", "sup")
        registerIntent(
            IntentType.CHECK_IN,
            "^(sup|wassup|watsup|whats\\s*up|what's\\s*up)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Not much, just ready and excited to chat with you! What's on your mind today?",
                "Hey! Standing by and ready to assist. What are you working on today?",
                "Not much at all! What can I help you with today?"
            )
        );

        // 8. Farewells
        registerIntent(
            IntentType.FAREWELL,
            "^(bye|goodbye|see\\s+ya|tc|take\\s+care|cya)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "Take care! Feel free to come back anytime you need help. 👋",
                "Goodbye! Have a fantastic day ahead! 👋",
                "See you later! I'm always here whenever you need assistance. 😊"
            )
        );

        // 9. Thanks / Acknowledgments
        registerIntent(
            IntentType.THANKS,
            "^(thank\\s*(you|u)+|thanks+|thx|ty|perfect|awesome|great)(\\s+(there|omega|bot|friend|buddy|brother|bro|dude|man|sir|maam|madam|dear))?[!?.]*$",
            Arrays.asList(
                "You're so very welcome! 😊 Always here for you whenever you need anything.",
                "Happy to help! Feel free to ask if you need anything else.",
                "Anytime! Let me know if you have any more questions. 👍"
            )
        );

        // 10. Task Listing Intent
        registerIntent(
            IntentType.TASK_LIST,
            "^(?:show|list|get|view|what\\s+are)\\s+(?:my\\s+)?(?:pending\\s+)?tasks?[!?.]*$",
            Collections.emptyList()
        );

        // 11. Note Listing Intent
        registerIntent(
            IntentType.NOTE_LIST,
            "^(?:show|list|get|view|what\\s+are)\\s+(?:my\\s+)?notes?[!?.]*$",
            Collections.emptyList()
        );

        // 12. Log Listing Intent
        registerIntent(
            IntentType.LOG_LIST,
            "^(?:show|list|view|get)\\s+(?:recent\\s+)?(?:chat\\s+)?logs?[!?.]*$|^what\\s+did\\s+we\\s+discuss\\s+earlier[!?.]*$",
            Collections.emptyList()
        );

        // 13. Identity
        registerIntent(
            IntentType.IDENTITY,
            "^(who|what)\\s+(are|is)\\s+(you|u|your\\s+name)[!?.]*$",
            Arrays.asList(
                "I'm **OMEGA**, your AI companion and intelligent assistant! 😊 How can I help you today?",
                "I'm **OMEGA**, your intelligent AI copilot. What would you like to work on today?"
            )
        );

        // 14. Capabilities
        registerIntent(
            IntentType.CAPABILITIES,
            "^(what\\s+can\\s+you\\s+do|help|capabilities|what\\s+are\\s+your\\s+features)[!?.]*$",
            Arrays.asList(
                "Here's what I can help you with:\n- 💻 **Code Generation**: Write and debug code in Python, Java, JS, C++, HTML/CSS\n- 🌾 **Agricultural ML**: Crop & Fertilizer predictions based on soil & climate\n- 📝 **Tasks & Notes**: Reminders, task tracking, and note-taking directly inline in chat!\n- 📜 **Chat History Logs**: View recent dialogue logs\n\nWhat can I do for you today?"
            )
        );
    }

    public IntentMatch process(String rawPrompt) {
        if (rawPrompt == null || rawPrompt.trim().isEmpty()) {
            return new IntentMatch(IntentType.UNKNOWN, null, false, "", "");
        }

        String prompt = rawPrompt.trim();
        String promptLower = prompt.toLowerCase();

        // 1. Check Task Creation
        Matcher taskCreateMatcher = taskCreatePattern.matcher(prompt);
        if (taskCreateMatcher.find()) {
            String rawTitle = taskCreateMatcher.group(1);
            String taskTitle = rawTitle != null ? rawTitle.trim() : "";
            if (!taskTitle.isEmpty()) {
                return new IntentMatch(IntentType.TASK_CREATE, null, false, "", "", taskTitle);
            }
        }

        // 2. Check Task Complete
        Matcher taskCompleteMatcher = taskCompletePattern.matcher(prompt);
        if (taskCompleteMatcher.find()) {
            String rawQuery = taskCompleteMatcher.group(1);
            String taskQuery = rawQuery != null ? rawQuery.trim() : "";
            if (!taskQuery.isEmpty()) {
                return new IntentMatch(IntentType.TASK_COMPLETE, null, false, "", "", taskQuery);
            }
        }

        // 3. Check Note Creation
        Matcher noteCreateMatcher = noteCreatePattern.matcher(prompt);
        if (noteCreateMatcher.find()) {
            String rawContent = noteCreateMatcher.group(1);
            String noteContent = rawContent != null ? rawContent.trim() : "";
            if (!noteContent.isEmpty()) {
                return new IntentMatch(IntentType.NOTE_CREATE, null, false, "", "", noteContent);
            }
        }

        // 4. Check Prompt Generation Intent
        Matcher promptGenMatcher = promptGenPattern.matcher(prompt);
        if (promptGenMatcher.find()) {
            String rawTopic = promptGenMatcher.group(1);
            String topic = rawTopic != null ? rawTopic.trim() : "";
            if (!topic.isEmpty()) {
                return new IntentMatch(IntentType.PROMPT_GEN, null, false, "", "", topic);
            }
        }

        // 4. Check Pure Intent Matches (Greetings, Task/Note/Log listing, etc.)
        for (Rule rule : rules) {
            if (rule.pattern.matcher(promptLower).matches()) {
                String selectedResponse = rule.responses.isEmpty() ? null : rule.responses.get(random.nextInt(rule.responses.size()));
                return new IntentMatch(rule.type, selectedResponse, false, "", "");
            }
        }

        // 5. Check Mixed Greeting + Query
        Matcher mixedMatcher = mixedGreetingPattern.matcher(prompt);
        if (mixedMatcher.find()) {
            String rawGreeting = mixedMatcher.group(1);
            String greetingWord = rawGreeting != null ? rawGreeting.toLowerCase() : "";
            String rawQuery = mixedMatcher.group(2);
            String remainingQuery = rawQuery != null ? rawQuery.trim() : "";
            if (!remainingQuery.isEmpty()) {
                String prefix = "Hello! 😊 ";
                if (greetingWord.startsWith("hello") || greetingWord.startsWith("helo") || greetingWord.startsWith("halo") || greetingWord.startsWith("hlo")) {
                    prefix = "Hii! 😊 ";
                } else if (greetingWord.startsWith("hi") || greetingWord.startsWith("hey") || greetingWord.startsWith("hy")) {
                    prefix = "Hello! 😊 ";
                } else if (greetingWord.contains("good morning") || greetingWord.equals("gm")) {
                    prefix = "Good morning! 😊 ";
                } else if (greetingWord.contains("good afternoon")) {
                    prefix = "Good afternoon! 😊 ";
                } else if (greetingWord.contains("good evening")) {
                    prefix = "Good evening! 😊 ";
                } else if (greetingWord.startsWith("yo") || greetingWord.startsWith("sup")) {
                    prefix = "Hey there! 👋 ";
                }

                return new IntentMatch(IntentType.GREETING, null, true, remainingQuery, prefix);
            }
        }

        return new IntentMatch(IntentType.UNKNOWN, null, false, prompt, "");
    }
}
