package com.example.demo.service;

import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

@Service
public class IncidentKnowledgeService {

    public enum IncidentType {
        PANDEMIC,
        DISASTER,
        EDUCATION,
        CYBERSECURITY,
        ECONOMIC,
        ENVIRONMENTAL,
        GENERAL_INCIDENT
    }

    public IncidentType classifyIncident(String promptLower) {
        if (promptLower == null) return IncidentType.GENERAL_INCIDENT;

        if (promptLower.contains("covid") || promptLower.contains("corona") || promptLower.contains("pandemic") ||
            promptLower.contains("epidemic") || promptLower.contains("virus") || promptLower.contains("ebola") ||
            promptLower.contains("mpox") || promptLower.contains("influenza") || promptLower.contains("vaccine") ||
            promptLower.contains("quarantine") || promptLower.contains("sars") || promptLower.contains("outbreak")) {
            return IncidentType.PANDEMIC;
        }

        if (promptLower.contains("earthquake") || promptLower.contains("flood") || promptLower.contains("cyclone") ||
            promptLower.contains("tsunami") || promptLower.contains("wildfire") || promptLower.contains("hurricane") ||
            promptLower.contains("disaster") || promptLower.contains("landslide") || promptLower.contains("avalanche") ||
            promptLower.contains("typhoon") || promptLower.contains("tornado") || promptLower.contains("evacuation")) {
            return IncidentType.DISASTER;
        }

        if (promptLower.contains("education") || promptLower.contains("school") || promptLower.contains("university") ||
            promptLower.contains("college") || promptLower.contains("exam") || promptLower.contains("student") ||
            promptLower.contains("teacher") || promptLower.contains("curriculum") || promptLower.contains("learning") ||
            promptLower.contains("online class") || promptLower.contains("remote learning") || promptLower.contains("academic")) {
            return IncidentType.EDUCATION;
        }

        if (promptLower.contains("cyber") || promptLower.contains("ransomware") || promptLower.contains("data breach") ||
            promptLower.contains("hack") || promptLower.contains("outage") || promptLower.contains("ddos") ||
            promptLower.contains("vulnerability") || promptLower.contains("malware") || promptLower.contains("phishing")) {
            return IncidentType.CYBERSECURITY;
        }

        if (promptLower.contains("recession") || promptLower.contains("inflation") || promptLower.contains("market crash") ||
            promptLower.contains("bank run") || promptLower.contains("supply chain") || promptLower.contains("economic crisis") ||
            promptLower.contains("financial crisis")) {
            return IncidentType.ECONOMIC;
        }

        if (promptLower.contains("heatwave") || promptLower.contains("drought") || promptLower.contains("oil spill") ||
            promptLower.contains("toxic leak") || promptLower.contains("climate emergency") || promptLower.contains("pollution incident")) {
            return IncidentType.ENVIRONMENTAL;
        }

        return IncidentType.GENERAL_INCIDENT;
    }

    public boolean isIncidentQuery(String promptLower) {
        if (promptLower == null) return false;
        String[] keywords = {
            "incident", "emergency", "crisis", "disaster", "pandemic", "outbreak", "epidemic",
            "earthquake", "flood", "cyclone", "wildfire", "tsunami", "hurricane", "evacuation",
            "covid", "corona", "virus", "education crisis", "remote learning", "school closure",
            "cyberattack", "data breach", "ransomware", "recession", "inflation", "heatwave", "drought"
        };
        for (String k : keywords) {
            if (promptLower.contains(k)) return true;
        }
        return false;
    }

    public String generateIncidentKnowledgeSynthesis(String prompt, String promptLower, IncidentType type) {
        StringBuilder sb = new StringBuilder();
        String cleanTopic = prompt.replaceAll("(?i)^(tell about|explain|describe|what is|how to handle|report on|details on)\\s+", "").trim();
        if (!cleanTopic.isEmpty()) {
            cleanTopic = Character.toUpperCase(cleanTopic.charAt(0)) + cleanTopic.substring(1);
        } else {
            cleanTopic = "Incident Analysis & Response";
        }

        switch (type) {
            case PANDEMIC:
                sb.append("### 🦠 OMEGA Pandemic & Public Health Intelligence Matrix\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Epidemiological Profile & Pathogen Classification\n");
                sb.append("• **Pathogen Dynamics**: Infectious biological agents (coronaviruses, influenza, filoviruses) transmit via respiratory droplets, aerosols, or direct contact.\n");
                sb.append("• **Global Surveillance Protocols**: Real-time genomic sequencing, R0 basic reproduction rate monitoring, and WHO international health emergency declarations (PHEIC).\n");
                sb.append("• **Clinical Manifestations**: Acute respiratory symptoms, systemic inflammation, fever, and secondary organ complications.\n\n");
                sb.append("#### II. Emergency Public Health Response Framework\n");
                sb.append("1. **Containment & Mitigation**: Rapid contact tracing, isolation protocols, targeted quarantines, and non-pharmaceutical interventions (masks, ventilation).\n");
                sb.append("2. **Medical Prophylaxis & Therapeutics**: Accelerated mRNA/viral vector vaccine development, monoclonal antibodies, and antiviral regimens.\n");
                sb.append("3. **Healthcare Infrastructure Management**: Surge capacity allocation, ICU ventilator distribution, and personal protective equipment (PPE) stockpiling.\n\n");
                sb.append("#### III. Global Public Health Reference Standards\n");
                sb.append("• **World Health Organization (WHO)**: [https://www.who.int/emergencies/diseases](https://www.who.int/emergencies/diseases)\n");
                sb.append("• **CDC Disease Outbreak Telemetry**: [https://www.cdc.gov/outbreaks/index.html](https://www.cdc.gov/outbreaks/index.html)\n");
                break;

            case DISASTER:
                sb.append("### 🌪️ OMEGA Disaster Management & Relief Operations Engine\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Geophysical & Hydrometeorological Event Assessment\n");
                sb.append("• **Hazard Classification**: Rapid structural seismic waves (Richter/Moment Magnitude), storm surge inundation, flash flooding, or rapid ignition wildfire perimeters.\n");
                sb.append("• **Impact Telemetry**: Infrastructure integrity checks, population displacement metrics, critical utility disruption (power grid, water supply).\n\n");
                sb.append("#### II. Standard Emergency Operating Procedure (EOP)\n");
                sb.append("1. **Search & Rescue (USAR)**: Deployment of heavy urban search and rescue units, acoustic sensors, and drone thermal mapping.\n");
                sb.append("2. **Evacuation & Sheltering**: Activation of pre-designated emergency shelters, supply chain logistics for potable water, rations, and medical trauma kits.\n");
                sb.append("3. **Disaster Risk Reduction (DRR)**: Early warning siren networks, seismic retrofitting, and satellite radar monitoring (USGS / NOAA / NDMA).\n\n");
                sb.append("#### III. Authoritative Disaster Telemetry Resources\n");
                sb.append("• **USGS Earthquake & Geological Hazards**: [https://www.usgs.gov/programs/earthquake-hazards](https://www.usgs.gov/programs/earthquake-hazards)\n");
                sb.append("• **FEMA Disaster Relief Portal**: [https://www.fema.gov/disaster](https://www.fema.gov/disaster)\n");
                sb.append("• **Global Disaster Alert & Coordination System (GDACS)**: [https://www.gdacs.org](https://www.gdacs.org)\n");
                break;

            case EDUCATION:
                sb.append("### 🎓 OMEGA Educational Continuity & Academic Crisis Framework\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Crisis Impact on Educational Systems\n");
                sb.append("• **Institutional Operational Risk**: Physical school closures, disruption to standardized examination cycles, digital divide equity gaps, and student mental health pressures.\n");
                sb.append("• **Pedagogical Adaptations**: Synchronous vs asynchronous remote learning models, hybrid classroom deployment, and resilient LMS (Learning Management Systems).\n\n");
                sb.append("#### II. Academic Resiliency & Strategic Execution Plan\n");
                sb.append("1. **Infrastructure Provisioning**: Zero-rated educational data access, cloud classroom infrastructure, and offline digital content delivery.\n");
                sb.append("2. **Assessment Integrity**: Proctored online examinations, continuous formative evaluation, and flexible credit transfer policies.\n");
                sb.append("3. **Faculty & Student Support**: Mental health support hotlines, rapid digital literacy training, and socio-economic support programs.\n\n");
                sb.append("#### III. Educational Policy & Global Standards\n");
                sb.append("• **UNESCO Crisis Education Response**: [https://www.unesco.org/en/education/emergencies](https://www.unesco.org/en/education/emergencies)\n");
                sb.append("• **Global Partnership for Education (GPE)**: [https://www.globalpartnership.org](https://www.globalpartnership.org)\n");
                break;

            case CYBERSECURITY:
                sb.append("### 🛡️ OMEGA Cybersecurity Incident Response & Threat Matrix\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Threat Vector & Attack Vector Taxonomy\n");
                sb.append("• **Attack Vectors**: Ransomware execution, zero-day exploit payload, distributed denial-of-service (DDoS), credential dumping, or supply chain compromise.\n");
                sb.append("• **Threat Actor Profile**: Nation-state APTs, cybercrime syndicates, or insider threats executing lateral movement across enterprise subnets.\n\n");
                sb.append("#### II. NIST SP 800-61 Rev. 2 Incident Handling Lifecycle\n");
                sb.append("1. **Preparation**: Immutable data backups, zero-trust network access (ZTNA), and multi-factor authentication (MFA) enforcement.\n");
                sb.append("2. **Detection & Containment**: SIEM telemetry ingestion, isolation of affected host segments, firewall rule updates, and memory forensics.\n");
                sb.append("3. **Eradication & Recovery**: Malware artifact destruction, system restoration from clean snapshots, and post-incident root cause analysis (RCA).\n\n");
                sb.append("#### III. Cyber Threat Intelligence Sources\n");
                sb.append("• **CISA Known Exploited Vulnerabilities**: [https://www.cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)\n");
                sb.append("• **MITRE ATT&CK Matrix**: [https://attack.mitre.org](https://attack.mitre.org)\n");
                break;

            case ECONOMIC:
                sb.append("### 📈 OMEGA Macroeconomic Crisis & Financial Intelligence Engine\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Macroeconomic Stress Parameters\n");
                sb.append("• **Systemic Shock**: Supply chain bottlenecks, inflationary spikes, central bank interest rate shocks, or sovereign debt defaults.\n");
                sb.append("• **Market Liquidity Telemetry**: Asset devaluation, currency volatility, credit spread widening, and consumer sentiment contraction.\n\n");
                sb.append("#### II. Crisis Mitigation Strategy\n");
                sb.append("1. **Monetary Policy Stabilization**: Central bank liquidity injection, interest rate adjustments, and quantitative easing/tightening recalibration.\n");
                sb.append("2. **Fiscal Stimulus & Safety Nets**: Target subsidies, unemployment support, and strategic commodity stockpiling.\n");
                sb.append("3. **Supply Chain Resilience**: Nearshoring essential manufacturing, diversifying raw material sourcing, and logistics optimization.\n\n");
                sb.append("#### III. Global Economic Telemetry Portals\n");
                sb.append("• **International Monetary Fund (IMF) Reports**: [https://www.imf.org/en/Data](https://www.imf.org/en/Data)\n");
                sb.append("• **World Bank Global Economic Prospects**: [https://www.worldbank.org/en/publication/global-economic-prospects](https://www.worldbank.org/en/publication/global-economic-prospects)\n");
                break;

            case ENVIRONMENTAL:
                sb.append("### 🌿 OMEGA Environmental Crisis & Climate Security Intelligence\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Environmental Hazard Telemetry\n");
                sb.append("• **Incident Manifestations**: Extreme heatwaves, prolonged drought, chemical/industrial effluent spills, or marine ecosystem degradation.\n");
                sb.append("• **Ecological Risk Assessment**: Toxicity indexing, air quality index (AQI) spikes, groundwater contamination, and bioaccumulation factors.\n\n");
                sb.append("#### II. Remediation & Environmental Emergency Response\n");
                sb.append("1. **Containment & Neutralization**: Chemical containment booms, soil remediation, and hazardous material (HAZMAT) response deployment.\n");
                sb.append("2. **Resource Preservation**: Emergency water rationing, power grid load shedding during heatwaves, and wildlife habitat protection.\n");
                sb.append("3. **Long-Term Climate Resilience**: Reforestation, renewable energy transition, and carbon capture infrastructure.\n\n");
                sb.append("#### III. Environmental Reference Portals\n");
                sb.append("• **United Nations Environment Programme (UNEP)**: [https://www.unep.org](https://www.unep.org)\n");
                sb.append("• **US EPA Environmental Emergency Management**: [https://www.epa.gov/emergency-response](https://www.epa.gov/emergency-response)\n");
                break;

            default:
                sb.append("### 🌐 OMEGA Incident Intelligence & Crisis Management Matrix\n\n");
                sb.append("**Incident Focus**: *\"").append(cleanTopic).append("\"*\n\n");
                sb.append("#### I. Universal Incident Assessment & Situational Awareness\n");
                sb.append("• **Incident Severity Matrix**: Evaluating impact magnitude, affected population/assets, and operational escalation triggers.\n");
                sb.append("• **Multi-Agency Coordination**: Establishing Unified Command System (ICS) protocols across technical, medical, and administrative responders.\n\n");
                sb.append("#### II. Core Emergency Action Lifecycle\n");
                sb.append("1. **Rapid Response**: Immediate triage, containment, and protective action deployment.\n");
                sb.append("2. **Resource Mobilization**: Supply chain activation, communications redundancy, and emergency personnel dispatch.\n");
                sb.append("3. **Post-Incident Recovery**: Infrastructure restoration, lessons learned debriefing, and resilience upgrading.\n\n");
                sb.append("#### III. Reference Authorities\n");
                sb.append("• **United Nations Office for Disaster Risk Reduction (UNDRR)**: [https://www.undrr.org](https://www.undrr.org)\n");
                break;
        }

        return sb.toString();
    }
}
