package com.example.demo.intent;

public class IntentMatch {
    private final IntentType intentType;
    private final String response;
    private final boolean isMixed;
    private final String remainingQuery;
    private final String greetingPrefix;
    private final String payload;

    public IntentMatch(IntentType intentType, String response, boolean isMixed, String remainingQuery, String greetingPrefix) {
        this(intentType, response, isMixed, remainingQuery, greetingPrefix, null);
    }

    public IntentMatch(IntentType intentType, String response, boolean isMixed, String remainingQuery, String greetingPrefix, String payload) {
        this.intentType = intentType;
        this.response = response;
        this.isMixed = isMixed;
        this.remainingQuery = remainingQuery;
        this.greetingPrefix = greetingPrefix;
        this.payload = payload;
    }

    public boolean isMatched() {
        return intentType != IntentType.UNKNOWN;
    }

    public IntentType getIntentType() {
        return intentType;
    }

    public String getResponse() {
        return response;
    }

    public boolean isMixed() {
        return isMixed;
    }

    public String getRemainingQuery() {
        return remainingQuery;
    }

    public String getGreetingPrefix() {
        return greetingPrefix;
    }

    public String getPayload() {
        return payload;
    }
}
