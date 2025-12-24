import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Check, AlertTriangle } from 'lucide-react'

const methods = [
  {
    name: 'IVW',
    fullName: 'Inverse Variance Weighted',
    description: 'Weighted average of per-SNP estimates. Most efficient when all instruments are valid.',
    pros: ['Highest statistical power', 'Simple to interpret', 'Default method'],
    cons: ['Biased if any SNP violates assumptions', 'No pleiotropy test'],
    robustness: 1,
    power: 5,
    complexity: 1,
  },
  {
    name: 'Weighted Median',
    fullName: 'Weighted Median Estimator',
    description: 'Takes the median of per-SNP estimates. Robust if >50% of instruments are valid.',
    pros: ['Robust to up to 50% invalid instruments', 'Still interpretable'],
    cons: ['Lower power than IVW', 'Assumes majority valid'],
    robustness: 3,
    power: 3,
    complexity: 2,
  },
  {
    name: 'MR-Egger',
    fullName: 'MR-Egger Regression',
    description: 'Allows for pleiotropy via an intercept term. Tests for directional pleiotropy.',
    pros: ['Detects directional pleiotropy', 'Provides pleiotropy test'],
    cons: ['Low power', 'Assumes InSIDE', 'Wide confidence intervals'],
    robustness: 4,
    power: 2,
    complexity: 3,
  },
  {
    name: 'MR-PRESSO',
    fullName: 'Pleiotropy Residual Sum and Outlier',
    description: 'Detects and removes outlier SNPs, then re-estimates the causal effect.',
    pros: ['Identifies specific outliers', 'Corrected estimate available'],
    cons: ['Computationally intensive', 'May remove valid SNPs'],
    robustness: 4,
    power: 4,
    complexity: 4,
  },
  {
    name: 'Contamination Mixture',
    fullName: 'Contamination Mixture Model',
    description: 'Models SNPs as mixture of valid and invalid instruments using EM algorithm.',
    pros: ['Probabilistic framework', 'Soft outlier handling'],
    cons: ['Complex to interpret', 'Requires many SNPs'],
    robustness: 5,
    power: 3,
    complexity: 5,
  },
  {
    name: 'Bayesian MR',
    fullName: 'Bayesian Mendelian Randomization',
    description: 'Full posterior inference with prior incorporation. Returns credible intervals.',
    pros: ['Full uncertainty quantification', 'Prior incorporation', 'Bayes factors'],
    cons: ['Computationally expensive', 'Requires prior specification'],
    robustness: 4,
    power: 4,
    complexity: 5,
  },
]

const chartData = methods.map(m => ({
  name: m.name,
  robustness: m.robustness,
  power: m.power,
  complexity: m.complexity,
}))

export function MethodsComparison() {
  return (
    <section className="section">
      <h2>MR Methods Comparison</h2>
      <p className="intro">
        Different methods make different assumptions. Choose based on your data quality and research question.
      </p>

      <div className="methods-chart">
        <h4>Method Characteristics (1-5 scale)</h4>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 5]} tickCount={6} label={{ value: 'Rating (1=Low, 5=High)', position: 'bottom', offset: 0 }} />
            <YAxis type="category" dataKey="name" />
            <Tooltip />
            <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 10 }} />
            <Bar dataKey="robustness" name="Robustness to Pleiotropy" fill="#10B981" />
            <Bar dataKey="power" name="Statistical Power" fill="#3B82F6" />
            <Bar dataKey="complexity" name="Complexity" fill="#F59E0B" />
          </BarChart>
        </ResponsiveContainer>
        <p className="table-note">
          Robustness = how well the method handles invalid instruments; Power = ability to detect true effects; Complexity = computational/interpretive difficulty.
        </p>
      </div>

      <div className="methods-grid">
        {methods.map((method) => (
          <div key={method.name} className="method-card">
            <h4>{method.name}</h4>
            <p className="method-fullname">{method.fullName}</p>
            <p className="method-desc">{method.description}</p>

            <div className="method-pros-cons">
              <div className="pros">
                {method.pros.map((pro, i) => (
                  <span key={i} className="pro-item">
                    <Check size={14} /> {pro}
                  </span>
                ))}
              </div>
              <div className="cons">
                {method.cons.map((con, i) => (
                  <span key={i} className="con-item">
                    <AlertTriangle size={14} /> {con}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="decision-guide">
        <h3>When to Use Each Method</h3>
        <table className="decision-table">
          <thead>
            <tr>
              <th>Scenario</th>
              <th>Recommended Method</th>
              <th>Why</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>High-quality, validated instruments</td>
              <td><strong>IVW</strong></td>
              <td>Maximum power when assumptions hold</td>
            </tr>
            <tr>
              <td>Suspected pleiotropy, many SNPs</td>
              <td><strong>MR-PRESSO + Weighted Median</strong></td>
              <td>Remove outliers, confirm with robust method</td>
            </tr>
            <tr>
              <td>Testing for directional pleiotropy</td>
              <td><strong>MR-Egger</strong></td>
              <td>Intercept provides pleiotropy test</td>
            </tr>
            <tr>
              <td>Uncertainty quantification needed</td>
              <td><strong>Bayesian MR</strong></td>
              <td>Full posterior, credible intervals, Bayes factors</td>
            </tr>
            <tr>
              <td>Unknown proportion invalid</td>
              <td><strong>Contamination Mixture</strong></td>
              <td>EM estimates validity probability per SNP</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}
