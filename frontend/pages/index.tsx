import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const INDUSTRIES = [
  "",
  "AgriTech",
  "AI / ML",
  "BioTech",
  "ClimateTech",
  "E-Commerce",
  "EdTech",
  "FinTech",
  "HealthTech",
  "HRTech",
  "InsurTech",
  "LegalTech",
  "Logistics",
  "MarTech",
  "PropTech",
  "SaaS",
  "Social Impact",
  "SportsTech",
];

interface AnalyzeResult {
  idea: string;
  industry: string;
  target_audience: string;
  country: string;
  score: number;
  verdict: string;
  market_size_estimate: string;
  competition_level: string;
  strengths: string[];
  risks: string[];
  suggestions: string[];
}

export default function Home() {
  const [idea, setIdea] = useState("");
  const [industry, setIndustry] = useState("");
  const [audience, setAudience] = useState("");
  const [country, setCountry] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea, industry, target_audience: audience, country }),
      });
      setResult(await res.json());
    } catch {
      alert("Backend unreachable. Ensure the API server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-violet-300 to-fuchsia-300 bg-clip-text text-transparent">
          Startup Validator
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Describe your idea and get instant AI-powered feedback.
        </p>
      </div>

      {/* Form Card */}
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-2xl bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 shadow-2xl space-y-6"
      >
        {/* Idea */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Startup Idea
          </label>
          <textarea
            rows={4}
            placeholder="Describe your startup idea in detail..."
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            required
          />
        </div>

        {/* Industry */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Industry
          </label>
          <select
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent appearance-none cursor-pointer"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          >
            <option value="" disabled className="bg-slate-800">
              Select an industry
            </option>
            {INDUSTRIES.filter(Boolean).map((ind) => (
              <option key={ind} value={ind} className="bg-slate-800">
                {ind}
              </option>
            ))}
          </select>
        </div>

        {/* Audience + Country row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Target Audience
            </label>
            <input
              placeholder="e.g. Small business owners"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Country
            </label>
            <input
              placeholder="e.g. India, USA, UK"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            />
          </div>
        </div>

        {/* Button */}
        <button
          type="submit"
          disabled={loading || !idea.trim()}
          className="w-full bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white font-semibold py-3.5 rounded-xl transition-all duration-200 flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <span className="inline-block h-5 w-5 rounded-full border-2 border-white/30 border-t-white loader-ring" />
              Validating...
            </>
          ) : (
            "Validate Idea"
          )}
        </button>
      </form>

      {/* Result Dashboard */}
      {result && (
        <div className="w-full max-w-2xl mt-10 space-y-4">
          {/* Score + Meta row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <ResultCard
              title="Score"
              delay={0}
            >
              <div className="flex flex-col items-center justify-center h-full">
                <span className="text-4xl font-extrabold text-white">{result.score}/100</span>
                <span
                  className={`mt-1 text-sm font-medium ${
                    result.verdict === "Promising"
                      ? "text-emerald-400"
                      : result.verdict === "Needs refinement"
                      ? "text-amber-400"
                      : "text-rose-400"
                  }`}
                >
                  {result.verdict}
                </span>
              </div>
            </ResultCard>

            <ResultCard title="Market Size" delay={100}>
              <div className="flex flex-col items-center justify-center h-full">
                <span className="text-2xl font-bold text-violet-300">{result.market_size_estimate}</span>
              </div>
            </ResultCard>

            <ResultCard title="Competition" delay={200}>
              <div className="flex flex-col items-center justify-center h-full">
                <span
                  className={`text-2xl font-bold ${
                    result.competition_level === "Low"
                      ? "text-emerald-400"
                      : result.competition_level === "Medium"
                      ? "text-amber-400"
                      : "text-rose-400"
                  }`}
                >
                  {result.competition_level}
                </span>
              </div>
            </ResultCard>
          </div>

          {/* Strengths / Risks / Suggestions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ListCard title="Strengths" items={result.strengths} color="emerald" delay={300} />
            <ListCard title="Risks" items={result.risks} color="rose" delay={400} />
            <ListCard title="Suggestions" items={result.suggestions} color="violet" delay={500} />
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Generic card wrapper ─── */
function ResultCard({
  title,
  delay,
  children,
}: {
  title: string;
  delay: number;
  children: React.ReactNode;
}) {
  return (
    <div
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 min-h-[110px] animate-fade-in"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

/* ─── List card ─── */
function ListCard({
  title,
  items,
  color,
  delay,
}: {
  title: string;
  items: string[];
  color: "emerald" | "rose" | "violet";
  delay: number;
}) {
  const dot = {
    emerald: "bg-emerald-400",
    rose: "bg-rose-400",
    violet: "bg-violet-400",
  };
  return (
    <div
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 min-h-[140px] animate-fade-in"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
        {title}
      </h3>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dot[color]}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
