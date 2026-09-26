package com.example.demo.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class WebSearchServiceTest {

    private final WebSearchService service = new WebSearchService();

    @Test
    void routesRealtimeMarketAndSportsQueries() {
        assertTrue(service.isRealTimeSearchIntent("USD to INR exchange rate"));
        assertTrue(service.isRealTimeSearchIntent("What is USD to INR exchange rate?"));
        assertTrue(service.isRealTimeSearchIntent("Potato bhav in Agra mandi"));
        assertTrue(service.isRealTimeSearchIntent("What is the current cricket score?"));
    }

    @Test
    void keepsStableGeneralKnowledgeOutOfRealtimePath() {
        assertFalse(service.isRealTimeSearchIntent("What is the capital of Australia?"));
    }
}