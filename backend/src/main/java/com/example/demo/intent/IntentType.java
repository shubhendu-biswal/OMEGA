package com.example.demo.intent;

public enum IntentType {
    GREETING,
    WELLBEING,
    CHECK_IN,
    FAREWELL,
    THANKS,
    IDENTITY,
    CAPABILITIES,
    
    // Unified Chat Intent Extensions
    TASK_CREATE,
    TASK_LIST,
    TASK_COMPLETE,
    NOTE_CREATE,
    NOTE_LIST,
    LOG_LIST,

    // Prompt Engineering Intent
    PROMPT_GEN,

    UNKNOWN
}
