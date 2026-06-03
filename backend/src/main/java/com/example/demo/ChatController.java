package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.example.demo.repository.IndiaGkDataRepository;
import com.example.demo.model.IndiaGkData;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api")
public class ChatController {

    @Autowired
    private IndiaGkDataRepository indiaGkDataRepository;

    @PostMapping("/chat")
    public ResponseEntity<?> handleChat(@RequestBody ChatRequest request) {
        String prompt = request.getPrompt();
        String agent = request.getAgent();
        if (prompt == null) {
            prompt = "";
        }
        if (agent == null) {
            agent = "Nexus Core";
        }

        String promptLower = prompt.toLowerCase();
        String reply = "";

        // Check if query is related to ML/DL models (crop prediction or fertilizer recommendation)
        boolean isCropQuery = promptLower.contains("crop") && (promptLower.contains("predict") || promptLower.contains("recommend") || promptLower.contains("suggest"));
        boolean isFertilizerQuery = promptLower.contains("fertilizer") && (promptLower.contains("predict") || promptLower.contains("recommend") || promptLower.contains("suggest"));
        boolean hasSoilOrTemp = promptLower.contains("soil") || promptLower.contains("temp") || promptLower.contains("celsius") || promptLower.contains("degree");

        if (isCropQuery || isFertilizerQuery || hasSoilOrTemp) {
            // Parse Soil
            String parsedSoil = null;
            String[] soils = {
                "Alkaline", "Alluvial", "Black", "Brown", "Chalky", "Chernozem", "Clayey", "Desert",
                "Forest", "Gravelly", "Laterite", "Lateritic", "Loamy", "Marshy", "Mediterranean",
                "Mountain", "Peaty", "Permafrost", "Podzol", "Red", "Saline", "Sandy", "Silty",
                "Tundra", "Volcanic", "Yellow"
            };
            for (String s : soils) {
                if (promptLower.contains(s.toLowerCase())) {
                    parsedSoil = s;
                    break;
                }
            }
            if (parsedSoil == null && (promptLower.contains("clay") || promptLower.contains("clayey"))) {
                parsedSoil = "Clayey";
            }

            // Parse Temperature
            Double parsedTemp = null;
            Pattern tempPattern = Pattern.compile("\\b(\\d+(?:\\.\\d+)?)\\s*(?:°c|celsius|degrees|temp)?\\b");
            Matcher tempMatcher = tempPattern.matcher(promptLower);
            while (tempMatcher.find()) {
                try {
                    double val = Double.parseDouble(tempMatcher.group(1));
                    if (val >= 0 && val <= 60) {
                        parsedTemp = val;
                        break;
                    }
                } catch (NumberFormatException e) {
                    // ignore
                }
            }

            // Parse Crop
            String parsedCrop = null;
            String[] crops = {
                "Almond", "Apple", "Arecanut", "Avocado", "Bamboo", "Banana", "Barley", "Barnyard Millet",
                "Beetroot", "Bitter Gourd", "Blackgram", "Bottle Gourd", "Brinjal", "Broccoli", "Cabbage",
                "Capsicum", "Carrot", "Cashew", "Cauliflower", "Chickpea", "Chili", "Cocoa", "Coconut",
                "Coffee", "Coriander", "Cotton", "Cowpea", "Cucumber", "Custard Apple", "Dragon Fruit",
                "Fig", "Finger Millet", "Flax", "Foxtail Millet", "Garlic", "Ginger", "Grapes", "Green Gram",
                "Groundnut", "Guava", "Horse Gram", "Jackfruit", "Jute", "Kidneybeans", "Kodo Millet",
                "Lentil", "Little Millet", "Lychee", "Maize", "Mango", "Millet", "Mint", "Mungbean",
                "Muskmelon", "Mustard", "Oats", "Onion", "Orange", "Papaya", "Peas", "Pearl Millet",
                "Pigeonpeas", "Pineapple", "Pomegranate", "Potato", "Pumpkin", "Quinoa", "Radish", "Rice",
                "Rubber", "Rye", "Saffron", "Sapota", "Sesame", "Sorghum", "Soybean", "Spinach", "Strawberry",
                "Sugarcane", "Sunflower", "Sweet Potato", "Tapioca", "Tea", "Tea Leaves", "Tobacco",
                "Tomato", "Turmeric", "Walnut", "Watermelon", "Wheat"
            };
            for (String c : crops) {
                if (promptLower.contains(c.toLowerCase())) {
                    parsedCrop = c;
                    break;
                }
            }

            // 1. Fertilizer Recommendation Request (Check this first to prevent crop keyword overlap)
            if (isFertilizerQuery || (parsedTemp != null && parsedSoil != null && parsedCrop != null)) {
                if (parsedTemp == null || parsedSoil == null || parsedCrop == null) {
                    reply = "### 🧪 OMEGA Agricultural Recommendation Engine (ML Model)\n" +
                            "To recommend the optimal fertilizer, please specify **temperature** (e.g., 28°C), **soil type** (e.g., Black soil), and the **crop** (e.g., Wheat or Maize).\n\n" +
                            "*Example prompt: \"Recommend fertilizer for 28°C on Sandy soil with Maize crop\"*";
                } else {
                    Map<String, Object> payload = new HashMap<>();
                    payload.put("temperature", parsedTemp);
                    payload.put("soil_type", parsedSoil);
                    payload.put("crop", parsedCrop);

                    Map<String, Object> response = callMlService("/predict-fertilizer", payload);
                    if (response != null && "success".equals(response.get("status"))) {
                        String recommendedFert = (String) response.get("recommended_fertilizer");

                        reply = "### 🧪 OMEGA Agricultural Recommendation Engine (ML Model)\n" +
                                "The Random Forest Classifier has formulated the optimal fertilizer recommendation:\n\n" +
                                "**Recommended Fertilizer**: **" + recommendedFert + "**\n\n" +
                                "*Parameters analyzed: Temperature: " + parsedTemp + "°C | Soil Type: " + parsedSoil + " | Crop: " + parsedCrop + "*";
                    } else {
                        reply = "### ⚠️ ML Service Error\n" +
                                "Connected to the ML gateway, but the Random Forest model failed to evaluate fertilizer options. Please check if the ML server is healthy.";
                    }
                }
            }
            // 2. Crop Prediction Request
            else if (isCropQuery || (parsedTemp != null && parsedSoil != null && parsedCrop == null)) {
                if (parsedTemp == null || parsedSoil == null) {
                    reply = "### 🌾 OMEGA Agricultural Prediction Engine (ML Model)\n" +
                            "To predict the best crop, please specify both **temperature** (e.g., 28°C) and **soil type** (e.g., Sandy, Clayey, Alluvial, Loamy).\n\n" +
                            "*Example prompt: \"Predict crop for 25°C on Clayey soil\"*";
                } else {
                    Map<String, Object> payload = new HashMap<>();
                    payload.put("temperature", parsedTemp);
                    payload.put("soil_type", parsedSoil);

                    Map<String, Object> response = callMlService("/predict-crop", payload);
                    if (response != null && "success".equals(response.get("status"))) {
                        String predCrop = (String) response.get("predicted_crop");
                        List<Map<String, Object>> topCrops = (List<Map<String, Object>>) response.get("top_crops");

                        StringBuilder sb = new StringBuilder();
                        sb.append("### 🌾 OMEGA Agricultural Prediction Engine (ML Model)\n");
                        sb.append("The Machine Learning Random Forest model has calculated the optimal crop selection:\n\n");
                        sb.append("**Recommended Crop**: **").append(predCrop).append("**\n\n");
                        sb.append("#### Top 3 Recommendations:\n");
                        sb.append("| Rank | Crop Recommendation | Confidence Probability |\n");
                        sb.append("|---|---|---|\n");
                        if (topCrops != null) {
                            int rank = 1;
                            for (Map<String, Object> tc : topCrops) {
                                sb.append("| ").append(rank++).append(" | ").append(tc.get("crop"))
                                  .append(" | ").append(tc.get("probability")).append("% |\n");
                            }
                        }
                        sb.append("\n*Parameters analyzed: Temperature: ").append(parsedTemp).append("°C | Soil Type: ").append(parsedSoil).append("*\n");
                        reply = sb.toString();
                    } else {
                        reply = "### ⚠️ ML Service Error\n" +
                                "Connected to the ML gateway, but the Random Forest model failed to evaluate crop options. Please check if the ML server is healthy.";
                    }
                }
            } else {
                reply = "Mainframe query received. Synthesizing agricultural parameters via Spring Boot REST backend:\n" +
                        "- **Detected Temperature**: " + (parsedTemp != null ? parsedTemp + "°C" : "None") + "\n" +
                        "- **Detected Soil**: " + (parsedSoil != null ? parsedSoil : "None") + "\n" +
                        "- **Detected Crop**: " + (parsedCrop != null ? parsedCrop : "None") + "\n\n" +
                        "Use prompts like: *\"Predict crop for 25°C on Clayey soil\"* or *\"Recommend fertilizer for 28°C on Sandy soil with Maize\"* to run the ML model.";
            }
        } else if (promptLower.contains("css") || promptLower.contains("ui") || promptLower.contains("design")) {
            reply = "Here is a custom glassmorphism layout specification matching your prompt details:\n\n" +
                    "```css\n" +
                    ".futuristic-card {\n" +
                    "  background: rgba(13, 20, 42, 0.45);\n" +
                    "  border: 1px solid rgba(0, 240, 255, 0.15);\n" +
                    "  backdrop-filter: blur(20px);\n" +
                    "  box-shadow: 0 8px 32px 0 rgba(0, 210, 255, 0.05);\n" +
                    "  border-radius: 16px;\n" +
                    "  padding: 24px;\n" +
                    "  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);\n" +
                    "}\n" +
                    ".futuristic-card:hover {\n" +
                    "  border-color: #00d2ff;\n" +
                    "  box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);\n" +
                    "  transform: translateY(-2px);\n" +
                    "}\n" +
                    "```\n" +
                    "- **Blur Filter**: 20px Gaussian depth.\n" +
                    "- **Hover Response**: Active glow projection.";
        } else if (promptLower.contains("react") || promptLower.contains("code") || promptLower.contains("leak")) {
            reply = "I have completed the state updater assessment for your React codebase:\n\n" +
                    "- **Anomaly Detected**: A potential stale closure inside the asynchronous `useEffect` state dispatch loop.\n" +
                    "- **Fidelity Mitigation**: Cleaned up active interval timers and wrapped listeners in a native `useCallback` hook.\n\n" +
                    "```jsx\n" +
                    "// Mitigation Refactoring\n" +
                    "const handleThreadRender = useCallback((threadId) => {\n" +
                    "  setThreadState(prev => {\n" +
                    "    const active = prev.find(t => t.id === threadId);\n" +
                    "    return active ? [...prev] : [...prev, { id: threadId, status: \"nominal\" }];\n" +
                    "  });\n" +
                    "}, []);\n" +
                    "```\n" +
                    "This resolves any race-conditions and prevents stale component renderings during automated updates.";
        } else {
            // Check if conversational greeting/phrase first
            String greetingResponse = handleConversationalGreeting(prompt);
            if (greetingResponse != null) {
                reply = greetingResponse;
            } else {
                // Query Flask ML Service for General Knowledge trained TF-IDF model first
                Map<String, Object> payload = new HashMap<>();
                payload.put("prompt", prompt);
                Map<String, Object> mlResponse = callMlService("/predict-gk", payload);
                
                if (mlResponse != null && "success".equals(mlResponse.get("status")) && mlResponse.get("answer") != null) {
                    reply = (String) mlResponse.get("answer");
                } else {
                    // Fallback to Oracle Text Search database query if ML model has no high confidence match
                    String searchQuery = buildSearchQuery(prompt);
                    List<IndiaGkData> matches = null;
                    if (searchQuery != null) {
                        try {
                            // Try with AND logic first (more specific)
                            matches = indiaGkDataRepository.searchByQuestionText(searchQuery, 1);
                            
                            // Fall back to OR logic if no match found
                            if ((matches == null || matches.isEmpty()) && searchQuery.contains(" AND ")) {
                                String orQuery = searchQuery.replace(" AND ", " OR ");
                                matches = indiaGkDataRepository.searchByQuestionText(orQuery, 1);
                            }
                        } catch (Exception e) {
                            System.err.println("Oracle Text Query error: " + e.getMessage());
                        }
                    }

                    if (matches != null && !matches.isEmpty()) {
                        IndiaGkData bestMatch = matches.get(0);
                        reply = bestMatch.getAnswer();
                    } else {
                        reply = "I searched our database of 1,000,000 India General Knowledge records, but no direct matches were found for your query. Please try asking in a different way.";
                    }
                }
            }
        }

        Map<String, Object> response = new HashMap<>();
        response.put("content", reply);
        response.put("agent", agent);
        response.put("timestamp", System.currentTimeMillis());

        return ResponseEntity.ok(response);
    }

    private String buildSearchQuery(String prompt) {
        if (prompt == null || prompt.trim().isEmpty()) {
            return null;
        }
        
        // Remove special punctuation/symbols that might break CONTAINS syntax
        String cleaned = prompt.replaceAll("[^a-zA-Z0-9\\s]", " ");
        String[] words = cleaned.split("\\s+");
        
        Set<String> stopWords = new HashSet<>(Arrays.asList(
            "what", "who", "where", "when", "why", "how", "which",
            "the", "a", "an", "and", "or", "but", "if", "then", "else",
            "of", "in", "on", "at", "to", "for", "from", "with", "by",
            "is", "was", "were", "are", "am", "be", "been", "being",
            "do", "does", "did", "has", "have", "had", "can", "could",
            "will", "would", "shall", "should", "about", "state", "indian", "india"
        ));
        
        List<String> validKeywords = new ArrayList<>();
        for (String w : words) {
            String lowerW = w.toLowerCase();
            if (lowerW.length() > 2 && !stopWords.contains(lowerW)) {
                validKeywords.add(w);
            }
        }
        
        if (validKeywords.isEmpty()) {
            return null;
        }
        
        // Join with AND
        return String.join(" AND ", validKeywords);
    }

    private String handleConversationalGreeting(String prompt) {
        if (prompt == null) {
            return null;
        }
        String clean = prompt.trim().toLowerCase().replaceAll("[^a-z0-9\\s]", "");
        
        // Greetings
        if (clean.equals("hi") || clean.equals("hii") || clean.equals("hello") || clean.equals("hey") || 
            clean.equals("hola") || clean.equals("greetings") || clean.equals("yo")) {
            return "Hello! I am OMEGA, your AI assistant. How can I help you today?";
        }
        
        if (clean.startsWith("good morning")) {
            return "Good morning! Hope you have a wonderful day. How can I assist you today?";
        }
        if (clean.startsWith("good afternoon")) {
            return "Good afternoon! How can I help you today?";
        }
        if (clean.startsWith("good evening")) {
            return "Good evening! How can I assist you today?";
        }

        // Well-being
        if (clean.contains("how are you") || clean.contains("how you doing") || clean.contains("hows it going")) {
            return "I am doing great, thank you! I am ready to answer your questions about Indian General Knowledge or provide crop recommendations. How can I help you today?";
        }

        // Identity / Name
        if (clean.contains("who are you") || clean.contains("what is your name") || clean.equals("name") || clean.contains("whats your name")) {
            return "I am OMEGA, a powerful AI assistant powered by Spring Boot and Oracle Database. I can help you with General Knowledge of India or agricultural recommendations.";
        }
        if (clean.contains("who created you") || clean.contains("who made you") || clean.contains("who programmed you")) {
            return "I was created and optimized by the OMEGA development team.";
        }
        if (clean.equals("omega") || clean.contains("what is omega")) {
            return "OMEGA is an advanced AI assistant system integrating Spring Boot REST services, an Oracle Database with over 1 million records, and Machine Learning gateways.";
        }

        // Appreciation
        if (clean.equals("thanks") || clean.contains("thank you") || clean.equals("ty") || clean.equals("perfect") || clean.equals("awesome") || clean.equals("great")) {
            return "You're very welcome! Let me know if you have any other questions.";
        }

        // Farewell
        if (clean.equals("bye") || clean.equals("goodbye") || clean.contains("see you") || clean.equals("tc") || clean.equals("take care")) {
            return "Goodbye! Have a great day ahead! Feel free to chat with me anytime you need assistance.";
        }

        return null;
    }

    private Map<String, Object> callMlService(String endpoint, Map<String, Object> payload) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            String jsonPayload = mapper.writeValueAsString(payload);

            HttpClient client = HttpClient.newHttpClient();
            HttpRequest httpRequest = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:5000" + endpoint))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

            HttpResponse<String> response = client.send(httpRequest, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                return mapper.readValue(response.body(), Map.class);
            }
        } catch (Exception e) {
            System.err.println("Failed to reach ML Flask service at localhost:5000: " + e.getMessage());
        }
        return null;
    }
}
