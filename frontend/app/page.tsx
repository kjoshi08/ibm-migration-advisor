"use client";

import { useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";
import {
  Server, Database, Shield, DollarSign,
  CheckCircle, AlertCircle, Clock, ChevronRight,
  Loader2, FileText, Activity, ArrowRight
} from "lucide-react";

const IBM_BLUE = "#0f62fe";
const IBM_GREEN = "#24a148";
const IBM_RED = "#da1e28";
const IBM_YELLOW = "#f1c21b";
const COLORS = [IBM_BLUE, IBM_GREEN, IBM_YELLOW, "#8a3ffc"];

type AgentStatus = "waiting" | "running" | "done" | "error";

interface AgentStep {
  id: number;
  name: string;
  description: string;
  status: AgentStatus;
}

const INITIAL_AGENTS: AgentStep[] = [
  {
    id: 1,
    name: "Infrastructure Analyser",
    description: "Reading and analysing your infrastructure",
    status: "waiting",
  },
  {
    id: 2,
    name: "RAG Retrieval Agent",
    description: "Searching IBM knowledge base",
    status: "waiting",
  },
  {
    id: 3,
    name: "Migration Planner",
    description: "Writing your IBM Cloud migration plan",
    status: "waiting",
  },
];

export default function Home() {
  const [clientName, setClientName] = useState("");
  const [infraDesc, setInfraDesc] = useState("");
  const [agents, setAgents] = useState<AgentStep[]>(INITIAL_AGENTS);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("plan");

  const updateAgent = (id: number, status: AgentStatus) => {
    setAgents((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status } : a))
    );
  };

  const runAnalysis = async () => {
    if (!clientName || !infraDesc) {
      setError("Please fill in all fields");
      return;
    }
    setError("");
    setResult(null);
    setLoading(true);
    setAgents(INITIAL_AGENTS);

    // Animate agents sequentially
    updateAgent(1, "running");
    await new Promise((r) => setTimeout(r, 2000));
    updateAgent(1, "done");

    updateAgent(2, "running");
    await new Promise((r) => setTimeout(r, 2000));
    updateAgent(2, "done");

    updateAgent(3, "running");

    try {
      const response = await axios.post("http://localhost:8000/analyse", {
        client_name: clientName,
        infrastructure_description: infraDesc,
      });

      updateAgent(3, "done");
      setResult(response.data);
    } catch (err: any) {
      updateAgent(3, "error");
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const getAgentIcon = (status: AgentStatus) => {
    if (status === "running")
      return <Loader2 size={16} className="animate-spin" color={IBM_BLUE} />;
    if (status === "done")
      return <CheckCircle size={16} color={IBM_GREEN} />;
    if (status === "error")
      return <AlertCircle size={16} color={IBM_RED} />;
    return <div style={{ width: 16, height: 16, borderRadius: "50%", background: "#e0e0e0" }} />;
  };

  const phaseData = result?.migration_plan?.phases?.map((p: any) => ({
    name: `Phase ${p.phase_number}`,
    weeks: p.duration_weeks,
    label: p.name,
  })) || [];

  const osData = result?.infra_summary?.operating_systems
    ? Object.entries(result.infra_summary.operating_systems)
        .filter(([, v]) => (v as number) > 0)
        .map(([k, v]) => ({ name: k, value: v as number }))
    : [];

  const tabs = ["plan", "analysis", "risks", "architecture", "costs", "quality"];

  return (
    <main style={{ minHeight: "calc(100vh - 48px)", background: "#f4f4f4" }}>
      {/* Hero */}
      <div style={{
        background: "linear-gradient(135deg, #0f62fe 0%, #0043ce 100%)",
        padding: "3rem 2rem",
        color: "white",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 8, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            IBM Cloud · AI-Powered
          </p>
          <h1 style={{ fontSize: 32, fontWeight: 300, marginBottom: 8 }}>
            Cloud Migration Advisor
          </h1>
          <p style={{ fontSize: 16, opacity: 0.8, fontWeight: 300 }}>
            Fine-tuned Llama 3 · LangGraph Agents · 30-second migration plans
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem" }}>
        {/* Input Card */}
        <div style={{
          background: "white",
          border: "1px solid #e0e0e0",
          padding: "2rem",
          marginBottom: "1.5rem",
        }}>
          <h2 style={{ fontSize: 18, fontWeight: 500, marginBottom: "1.5rem", color: "#161616" }}>
            Infrastructure Assessment
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "1rem", marginBottom: "1.5rem" }}>
            <div>
              <label style={{ fontSize: 12, fontWeight: 500, display: "block", marginBottom: 8, color: "#525252" }}>
                CLIENT NAME
              </label>
              <input
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="Acme Corporation"
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  border: "1px solid #8d8d8d",
                  fontSize: 14,
                  outline: "none",
                  fontFamily: "inherit",
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 500, display: "block", marginBottom: 8, color: "#525252" }}>
                INFRASTRUCTURE DESCRIPTION
              </label>
              <textarea
                value={infraDesc}
                onChange={(e) => setInfraDesc(e.target.value)}
                placeholder="20 servers: 12 Linux (Java apps), 8 Windows (.NET). 3 databases: 2 Oracle, 1 SQL Server. Critical apps: CustomerPortal, OrderManagement."
                rows={3}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  border: "1px solid #8d8d8d",
                  fontSize: 14,
                  outline: "none",
                  fontFamily: "inherit",
                  resize: "vertical",
                }}
              />
            </div>
          </div>

          {error && (
            <p style={{ color: IBM_RED, fontSize: 13, marginBottom: "1rem" }}>{error}</p>
          )}

          <button
            onClick={runAnalysis}
            disabled={loading}
            style={{
              background: loading ? "#8d8d8d" : IBM_BLUE,
              color: "white",
              border: "none",
              padding: "0.875rem 2rem",
              fontSize: 14,
              fontWeight: 500,
              cursor: loading ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontFamily: "inherit",
            }}
          >
            {loading ? (
              <><Loader2 size={16} className="animate-spin" /> Analysing Infrastructure...</>
            ) : (
              <>Run Migration Analysis <ArrowRight size={16} /></>
            )}
          </button>
        </div>

        {/* Agent Pipeline */}
        {(loading || result) && (
          <div style={{
            background: "white",
            border: "1px solid #e0e0e0",
            padding: "1.5rem",
            marginBottom: "1.5rem",
          }} className="animate-fade-in">
            <h3 style={{ fontSize: 14, fontWeight: 500, marginBottom: "1rem", color: "#525252", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              AI Agent Pipeline
            </h3>
            <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
              {agents.map((agent, idx) => (
                <div key={agent.id} style={{ display: "flex", alignItems: "center", flex: 1 }}>
                  <div style={{
                    flex: 1,
                    padding: "1rem",
                    background: agent.status === "done" ? "#defbe6" :
                                agent.status === "running" ? "#d0e2ff" :
                                agent.status === "error" ? "#fff1f1" : "#f4f4f4",
                    border: `1px solid ${
                      agent.status === "done" ? IBM_GREEN :
                      agent.status === "running" ? IBM_BLUE :
                      agent.status === "error" ? IBM_RED : "#e0e0e0"
                    }`,
                    transition: "all 0.3s ease",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      {getAgentIcon(agent.status)}
                      <span style={{ fontSize: 13, fontWeight: 500 }}>Agent {agent.id}</span>
                    </div>
                    <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 2 }}>{agent.name}</div>
                    <div style={{ fontSize: 11, color: "#525252" }}>{agent.description}</div>
                  </div>
                  {idx < agents.length - 1 && (
                    <ChevronRight size={20} color="#8d8d8d" style={{ flexShrink: 0 }} />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="animate-fade-in">
            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
              {[
                { icon: <Server size={20} color={IBM_BLUE} />, label: "Servers", value: result.infra_summary?.total_servers },
                { icon: <Database size={20} color={IBM_BLUE} />, label: "Databases", value: result.infra_summary?.total_databases },
                { icon: <Activity size={20} color={IBM_BLUE} />, label: "Complexity", value: `${result.infra_summary?.complexity_score}/10` },
                { icon: <FileText size={20} color={IBM_BLUE} />, label: "Phases", value: result.migration_plan?.phases?.length },
              ].map((stat, i) => (
                <div key={i} style={{ background: "white", border: "1px solid #e0e0e0", padding: "1.25rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    {stat.icon}
                    <span style={{ fontSize: 12, color: "#525252", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      {stat.label}
                    </span>
                  </div>
                  <div style={{ fontSize: 28, fontWeight: 300, color: "#161616" }}>{stat.value}</div>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div style={{ background: "white", border: "1px solid #e0e0e0" }}>
              <div style={{ display: "flex", borderBottom: "1px solid #e0e0e0", overflowX: "auto" }}>
                {tabs.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                      padding: "1rem 1.5rem",
                      border: "none",
                      borderBottom: activeTab === tab ? `2px solid ${IBM_BLUE}` : "2px solid transparent",
                      background: "none",
                      fontSize: 14,
                      fontWeight: activeTab === tab ? 500 : 400,
                      color: activeTab === tab ? IBM_BLUE : "#525252",
                      cursor: "pointer",
                      whiteSpace: "nowrap",
                      fontFamily: "inherit",
                      textTransform: "capitalize",
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div style={{ padding: "2rem" }}>
                {/* Plan Tab */}
                {activeTab === "plan" && (
                  <div>
                    <div style={{
                      background: "#f4f4f4",
                      borderLeft: `4px solid ${IBM_BLUE}`,
                      padding: "1rem 1.25rem",
                      marginBottom: "1.5rem",
                      fontSize: 14,
                      lineHeight: 1.7,
                    }}>
                      {result.migration_plan?.executive_summary}
                    </div>

                    <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Migration Phases</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {result.migration_plan?.phases?.map((phase: any) => (
                        <div key={phase.phase_number} style={{
                          border: "1px solid #e0e0e0",
                          padding: "1.25rem",
                        }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                            <div>
                              <span style={{
                                background: IBM_BLUE,
                                color: "white",
                                fontSize: 11,
                                padding: "2px 8px",
                                marginRight: 8,
                                fontWeight: 500,
                              }}>
                                Phase {phase.phase_number}
                              </span>
                              <span style={{ fontSize: 15, fontWeight: 500 }}>{phase.name}</span>
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: 4, color: "#525252", fontSize: 13 }}>
                              <Clock size={14} />
                              {phase.duration_weeks} weeks
                            </div>
                          </div>
                          <div style={{ marginBottom: "0.75rem" }}>
                            <div style={{ fontSize: 12, fontWeight: 500, color: "#525252", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>IBM Services</div>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                              {phase.ibm_services?.map((svc: string, i: number) => (
                                <span key={i} style={{
                                  background: "#d0e2ff",
                                  color: "#0043ce",
                                  fontSize: 12,
                                  padding: "2px 10px",
                                  fontWeight: 500,
                                }}>
                                  {svc}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 500, color: "#525252", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Activities</div>
                            {phase.activities?.map((act: string, i: number) => (
                              <div key={i} style={{ fontSize: 13, color: "#161616", marginBottom: 3, display: "flex", gap: 8 }}>
                                <span style={{ color: IBM_BLUE }}>›</span> {act}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analysis Tab */}
                {activeTab === "analysis" && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
                    <div>
                      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Phase Timeline (weeks)</h3>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={phaseData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip />
                          <Bar dataKey="weeks" fill={IBM_BLUE} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div>
                      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>OS Distribution</h3>
                      {osData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                          <PieChart>
                            <Pie data={osData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, value }) => `${name}: ${value}`}>
                              {osData.map((_: any, index: number) => (
                                <Cell key={index} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <div style={{ color: "#525252", fontSize: 14 }}>No OS data available</div>
                      )}
                    </div>
                    <div style={{ gridColumn: "1 / -1" }}>
                      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Infrastructure Summary</h3>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
                        {[
                          { label: "Migration Pattern", value: result.infra_summary?.migration_pattern },
                          { label: "Complexity Score", value: `${result.infra_summary?.complexity_score}/10` },
                          { label: "Migration Blockers", value: result.infra_summary?.migration_blockers?.length || 0 },
                        ].map((item, i) => (
                          <div key={i} style={{ background: "#f4f4f4", padding: "1rem", border: "1px solid #e0e0e0" }}>
                            <div style={{ fontSize: 12, color: "#525252", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>{item.label}</div>
                            <div style={{ fontSize: 20, fontWeight: 300 }}>{item.value}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Risks Tab */}
                {activeTab === "risks" && (
                  <div>
                    <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Risk Register</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {result.migration_plan?.risk_register?.map((risk: any, i: number) => (
                        <div key={i} style={{
                          border: "1px solid #e0e0e0",
                          padding: "1.25rem",
                          borderLeft: `4px solid ${
                            risk.likelihood === "high" ? IBM_RED :
                            risk.likelihood === "medium" ? IBM_YELLOW : IBM_GREEN
                          }`,
                        }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                            <span style={{ fontSize: 14, fontWeight: 500 }}>{risk.risk}</span>
                            <div style={{ display: "flex", gap: 8 }}>
                              <span style={{
                                fontSize: 11,
                                padding: "2px 8px",
                                fontWeight: 500,
                                background: risk.likelihood === "high" ? "#fff1f1" : risk.likelihood === "medium" ? "#fdf6dd" : "#defbe6",
                                color: risk.likelihood === "high" ? IBM_RED : risk.likelihood === "medium" ? "#805500" : IBM_GREEN,
                              }}>
                                {risk.likelihood?.toUpperCase()} LIKELIHOOD
                              </span>
                            </div>
                          </div>
                          <div style={{ fontSize: 13, color: "#525252", marginBottom: 8 }}>Impact: {risk.impact}</div>
                          <div style={{ fontSize: 13, color: "#161616" }}>
                            <span style={{ fontWeight: 500 }}>Mitigation: </span>{risk.mitigation}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Architecture Tab */}
                {activeTab === "architecture" && (
                  <div>
                    <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>IBM Cloud Target Architecture</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem" }}>
                      {result.migration_plan?.ibm_target_architecture &&
                        Object.entries(result.migration_plan.ibm_target_architecture).map(([key, value]: [string, any]) => (
                          <div key={key} style={{ border: "1px solid #e0e0e0", padding: "1.25rem" }}>
                            <div style={{ fontSize: 12, fontWeight: 500, color: IBM_BLUE, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                              {key}
                            </div>
                            <div style={{ fontSize: 14, color: "#161616" }}>{value}</div>
                          </div>
                        ))
                      }
                    </div>
                    <div style={{ marginTop: "1.5rem" }}>
                      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Compliance Checklist</h3>
                      {result.migration_plan?.compliance_checklist?.map((item: string, i: number) => (
                        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                          <CheckCircle size={16} color={IBM_GREEN} />
                          <span style={{ fontSize: 14 }}>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Costs Tab */}
                {activeTab === "costs" && result.migration_plan?.cost_estimate && (
                  <div>
                    <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1.5rem" }}>Cost Analysis</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
                      {[
                        { label: "Current Annual Cost", value: `$${result.migration_plan.cost_estimate.current_annual_cost_usd?.toLocaleString()}`, color: IBM_RED },
                        { label: "IBM Cloud Annual Cost", value: `$${result.migration_plan.cost_estimate.ibm_cloud_annual_cost_usd?.toLocaleString()}`, color: IBM_BLUE },
                        { label: "Migration Cost (one-time)", value: `$${result.migration_plan.cost_estimate.migration_one_time_cost_usd?.toLocaleString()}`, color: IBM_YELLOW },
                        { label: "3-Year Saving", value: `$${result.migration_plan.cost_estimate.three_year_saving_usd?.toLocaleString()}`, color: IBM_GREEN },
                      ].map((item, i) => (
                        <div key={i} style={{ border: "1px solid #e0e0e0", padding: "1.5rem", borderTop: `4px solid ${item.color}` }}>
                          <div style={{ fontSize: 12, color: "#525252", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>{item.label}</div>
                          <div style={{ fontSize: 28, fontWeight: 300, color: item.color }}>{item.value}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ background: "#defbe6", border: "1px solid #24a148", padding: "1.25rem", display: "flex", alignItems: "center", gap: 12 }}>
                      <DollarSign size={24} color={IBM_GREEN} />
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 500, color: "#0e6027" }}>
                          Total savings over 3 years
                        </div>
                        <div style={{ fontSize: 24, fontWeight: 600, color: IBM_GREEN }}>
                          {result.migration_plan.cost_estimate.saving_percentage}% cost reduction
                        </div>
                      </div>
                    </div>
                    <div style={{ marginTop: "1.5rem" }}>
                      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1rem" }}>Next Steps</h3>
                      {result.migration_plan?.next_steps?.map((step: string, i: number) => (
                        <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 12, padding: "1rem", background: "#f4f4f4", border: "1px solid #e0e0e0" }}>
                          <span style={{ background: IBM_BLUE, color: "white", width: 24, height: 24, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 600, flexShrink: 0 }}>
                            {i + 1}
                          </span>
                          <span style={{ fontSize: 14 }}>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quality Tab */}
                {activeTab === "quality" && (
                  <div>
                    <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: "1.5rem" }}>AI Quality Assurance</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
                      {[
                        { label: "Judge Score", value: `${result.eval_scores?.judge_score}/10`, color: IBM_BLUE },
                        { label: "Quality Status", value: result.eval_scores?.passed ? "PASSED" : "REVIEW NEEDED", color: result.eval_scores?.passed ? IBM_GREEN : IBM_RED },
                        { label: "Human Review", value: result.human_review_needed ? "Required" : "Not Required", color: result.human_review_needed ? IBM_YELLOW : IBM_GREEN },
                        { label: "Model", value: "Llama 3 RAFT", color: IBM_BLUE },
                      ].map((item, i) => (
                        <div key={i} style={{ border: "1px solid #e0e0e0", padding: "1.25rem" }}>
                          <div style={{ fontSize: 12, color: "#525252", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>{item.label}</div>
                          <div style={{ fontSize: 20, fontWeight: 500, color: item.color }}>{item.value}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ background: "#f4f4f4", border: "1px solid #e0e0e0", padding: "1.25rem" }}>
                      <div style={{ fontSize: 12, fontWeight: 500, color: "#525252", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
                        Fine-tuned Model Benchmark Results
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem" }}>
                        {[
                          { label: "ROUGE-L", value: "0.208", improvement: "+0.064" },
                          { label: "F1 Score", value: "0.263", improvement: "+0.058" },
                          { label: "Hallucination", value: "0.0%", improvement: "-3.3%" },
                          { label: "Judge Score", value: "9.1/10", improvement: "+1.2" },
                        ].map((m, i) => (
                          <div key={i} style={{ textAlign: "center" }}>
                            <div style={{ fontSize: 11, color: "#525252", textTransform: "uppercase", marginBottom: 4 }}>{m.label}</div>
                            <div style={{ fontSize: 20, fontWeight: 500, color: IBM_BLUE }}>{m.value}</div>
                            <div style={{ fontSize: 12, color: IBM_GREEN, fontWeight: 500 }}>{m.improvement} vs base</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={{
        background: "#161616",
        color: "#8d8d8d",
        padding: "1.5rem 2rem",
        fontSize: 12,
        marginTop: "3rem",
        display: "flex",
        justifyContent: "space-between",
      }}>
        <span>IBM Cloud Migration Advisor · AI Engineer — Hybrid Cloud & AI Division</span>
        <span>Fine-tuned Llama 3 · LangGraph · FastAPI · Next.js</span>
      </footer>
    </main>
  );
}
