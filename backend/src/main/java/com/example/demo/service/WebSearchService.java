package com.example.demo.service;

import org.springframework.stereotype.Service;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class WebSearchService {

    private final HttpClient httpClient;

    public WebSearchService() {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(8))
                .followRedirects(HttpClient.Redirect.NORMAL)
                .build();
    }

    public static class SearchResult {
        public String title;
        public String snippet;
        public String url;

        public SearchResult(String title, String snippet, String url) {
            this.title = title;
            this.snippet = snippet;
            this.url = url;
        }
    }

    public List<SearchResult> searchWeb(String query) {
        List<SearchResult> results = new ArrayList<>();
        if (query == null || query.trim().isEmpty()) {
            return results;
        }

        try {
            String encodedQuery = URLEncoder.encode(query.trim(), StandardCharsets.UTF_8);
            String searchUrl = "https://html.duckduckgo.com/html/?q=" + encodedQuery;

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(searchUrl))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    .header("Accept-Language", "en-US,en;q=0.9")
                    .timeout(Duration.ofSeconds(10))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                String html = response.body();
                results = parseDuckDuckGoHtml(html);
            }
        } catch (Exception e) {
            System.err.println("Live web search fetch warning: " + e.getMessage());
        }

        if (results.isEmpty()) {
            results = searchWikipedia(query);
        }

        return results;
    }

    private List<SearchResult> searchWikipedia(String query) {
        List<SearchResult> results = new ArrayList<>();
        try {
            String encodedQuery = URLEncoder.encode(query.trim(), StandardCharsets.UTF_8);
            String wikiUrl = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + encodedQuery + "&format=json";

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(wikiUrl))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OMEGA-AI/1.0")
                    .timeout(Duration.ofSeconds(6))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                String body = response.body();
                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                java.util.Map map = mapper.readValue(body, java.util.Map.class);
                java.util.Map queryMap = (java.util.Map) map.get("query");
                if (queryMap != null) {
                    java.util.List searchList = (java.util.List) queryMap.get("search");
                    if (searchList != null) {
                        int count = 0;
                        for (Object itemObj : searchList) {
                            if (count >= 5) break;
                            java.util.Map item = (java.util.Map) itemObj;
                            String title = (String) item.get("title");
                            String snippet = cleanHtml((String) item.get("snippet"));
                            if (title != null && !title.isEmpty()) {
                                String pageUrl = "https://en.wikipedia.org/wiki/" + URLEncoder.encode(title.replace(" ", "_"), StandardCharsets.UTF_8);
                                results.add(new SearchResult(title, snippet, pageUrl));
                                count++;
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("Wikipedia search fallback warning: " + e.getMessage());
        }
        return results;
    }

    public String fetchLiveWebPage(String targetUrl) {
        if (targetUrl == null || targetUrl.trim().isEmpty()) return null;
        try {
            String cleanUrl = targetUrl.trim();
            if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
                cleanUrl = "https://" + cleanUrl;
            }

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(cleanUrl))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    .timeout(Duration.ofSeconds(10))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                String body = response.body();
                String textOnly = cleanHtml(body);
                if (textOnly.length() > 3000) {
                    textOnly = textOnly.substring(0, 3000) + "... [Truncated]";
                }
                return textOnly;
            }
        } catch (Exception e) {
            System.err.println("Web page live fetch warning: " + e.getMessage());
        }
        return null;
    }

    private List<SearchResult> parseDuckDuckGoHtml(String html) {
        List<SearchResult> results = new ArrayList<>();
        if (html == null) return results;

        // Pattern matching result__a title & href
        Pattern resultPattern = Pattern.compile(
            "<a[^>]*class=\"result__a\"[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>.*?" +
            "(?:<a[^>]*class=\"result__snippet\"[^>]*>(.*?)</a>|<td[^>]*class=\"result-snippet\"[^>]*>(.*?)</td>)?",
            Pattern.DOTALL | Pattern.CASE_INSENSITIVE
        );

        Matcher matcher = resultPattern.matcher(html);
        int count = 0;
        while (matcher.find() && count < 5) {
            String rawUrl = matcher.group(1);
            String title = cleanHtml(matcher.group(2));
            String snippet1 = matcher.group(3);
            String snippet2 = matcher.group(4);
            String snippet = cleanHtml(snippet1 != null ? snippet1 : (snippet2 != null ? snippet2 : ""));

            String cleanUrlStr = extractCleanUrl(rawUrl);

            if (!title.isEmpty() && !cleanUrlStr.isEmpty()) {
                if (snippet.isEmpty()) {
                    snippet = "Live web result from " + cleanUrlStr;
                }
                results.add(new SearchResult(title, snippet, cleanUrlStr));
                count++;
            }
        }

        // Fallback: If combined regex yielded 0 results, extract result__a links directly
        if (results.isEmpty()) {
            Pattern simpleLinkPattern = Pattern.compile(
                "<a[^>]*class=\"result__a\"[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>",
                Pattern.DOTALL | Pattern.CASE_INSENSITIVE
            );
            Matcher simpleMatcher = simpleLinkPattern.matcher(html);
            while (simpleMatcher.find() && count < 5) {
                String rawUrl = simpleMatcher.group(1);
                String title = cleanHtml(simpleMatcher.group(2));
                String cleanUrlStr = extractCleanUrl(rawUrl);
                if (!title.isEmpty() && !cleanUrlStr.isEmpty()) {
                    results.add(new SearchResult(title, "Live real-time data from " + cleanUrlStr, cleanUrlStr));
                    count++;
                }
            }
        }

        return results;
    }

    public static String extractCleanUrl(String rawUrl) {
        if (rawUrl == null || rawUrl.trim().isEmpty()) return "";
        String url = rawUrl.trim();
        try {
            if (url.contains("uddg=")) {
                int idx = url.indexOf("uddg=");
                String param = url.substring(idx + 5);
                int ampIdx = param.indexOf("&");
                if (ampIdx != -1) {
                    param = param.substring(0, ampIdx);
                }
                url = java.net.URLDecoder.decode(param, StandardCharsets.UTF_8);
            } else if (url.startsWith("//")) {
                url = "https:" + url;
            }
        } catch (Exception e) {
            // fallback to original
        }
        return url;
    }

    public String extractUrlFromPrompt(String prompt) {
        if (prompt == null) return null;
        Pattern urlPattern = Pattern.compile("https?://[^\\s<]+|(?:www\\.)?[a-zA-Z0-9-]+\\.(?:com|org|net|gov|edu|io|co|in|ai|info)[^\\s<]*", Pattern.CASE_INSENSITIVE);
        Matcher matcher = urlPattern.matcher(prompt);
        if (matcher.find()) {
            return matcher.group(0);
        }
        return null;
    }

    private String cleanHtml(String text) {
        if (text == null) return "";
        return text.replaceAll("<script[^>]*>.*?</script>", " ")
                .replaceAll("<style[^>]*>.*?</style>", " ")
                .replaceAll("<[^>]*>", " ")
                .replaceAll("&quot;", "\"")
                .replaceAll("&amp;", "&")
                .replaceAll("&lt;", "<")
                .replaceAll("&gt;", ">")
                .replaceAll("&#x27;", "'")
                .replaceAll("&nbsp;", " ")
                .replaceAll("\\s+", " ")
                .trim();
    }

    public String buildSearchContext(List<SearchResult> results) {
        if (results.isEmpty()) {
            return "No live search results retrieved.";
        }
        StringBuilder sb = new StringBuilder();
        sb.append("=== LIVE WEB SEARCH RESULTS ===\n");
        int idx = 1;
        for (SearchResult r : results) {
            sb.append("[").append(idx++).append("] Title: ").append(r.title).append("\n");
            sb.append("    Snippet: ").append(r.snippet).append("\n");
            if (r.url != null && !r.url.isEmpty()) {
                sb.append("    Source URL: ").append(r.url).append("\n");
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    public boolean isRealTimeSearchIntent(String promptLower) {
        if (promptLower == null || promptLower.trim().isEmpty()) return false;
        String p = promptLower.trim();

        // 1. Explicit User Requests for Web Search (Rule 3)
        String[] explicitTriggers = {
            "search the web", "search google", "check online", "look it up",
            "find the latest", "browse the internet", "check the current information",
            "search web", "google search", "look online"
        };
        for (String et : explicitTriggers) {
            if (p.contains(et)) return true;
        }

        // 2. Stable Internal Knowledge Fast-Path Filter (Rule 1 & Rule 5)
        // If query asks for stable concepts/math/history without temporal indicators, bypass web search
        boolean containsFreshnessWord = p.contains("latest") || p.contains("today") || p.contains("now") ||
                                       p.contains("current") || p.contains("recent") || p.contains("2026") ||
                                       p.contains("this week") || p.contains("this month") || p.contains("news");

        if (!containsFreshnessWord) {
            // Stable math equations or basic calculations
            if (p.matches("^[0-9\\s\\+\\-\\*\\/\\^\\(\\)\\.]+$")) return false;

            // Stable explanations and definitions ("what is X", "who invented X", "explain X")
            if (p.startsWith("what is ") || p.startsWith("what are ") || p.startsWith("define ") ||
                p.startsWith("explain ") || p.startsWith("who invented ") || p.startsWith("when did ")) {
                boolean hasDynamicNoun = p.contains("price") || p.contains("stock") || p.contains("weather") ||
                                         p.contains("score") || p.contains("policy") || p.contains("office") ||
                                         p.contains("president") || p.contains("prime minister") || p.contains("ceo") ||
                                         p.contains("exchange rate") || p.contains("currency rate") || p.contains("forex") ||
                                         p.contains("mandi") || p.contains("bhav") || p.contains("apmc");
                if (!hasDynamicNoun) return false;
            }
        }

        // 3. Dynamic & Temporal Web Search Triggers (Rule 2)
        String[] realTimeKeywords = {
            "latest", "today", "now", "current", "recent", "this week", "this month", "2026",
            "news", "weather", "stock price", "price of", "crypto", "sports score", "score",
            "exchange rate", "currency rate", "forex", "mandi", "bhav", "apmc", "cricket score", "live score",
            "current prime minister", "current president", "current policy", "current laws",
            "current specs", "latest software", "latest gpu", "latest release", "trending",
            "match today", "who is the current", "what is the current", "browser", "url", "website"
        };

        for (String rtk : realTimeKeywords) {
            if (p.contains(rtk)) return true;
        }

        return p.split("\\s+").length >= 3 && containsFreshnessWord;
    }
}
