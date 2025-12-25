import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import * as Tabs from '@radix-ui/react-tabs'
import { Dna, GitBranch, Target, BarChart3, BookOpen, History, FlaskConical } from 'lucide-react'
import { MRDiagram } from './components/MRDiagram'
import { InteractiveDemo } from './components/InteractiveDemo'
import { MethodsComparison } from './components/MethodsComparison'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('concept')

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Dna className="logo-icon" />
            <h1>PyMR</h1>
          </div>
          <p className="tagline">Mendelian Randomization in Python</p>
        </div>
      </header>

      <main className="main">
        <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
          <Tabs.List className="tabs-list">
            <Tabs.Trigger value="concept" className="tab-trigger">
              <BookOpen size={18} />
              <span>What is MR?</span>
            </Tabs.Trigger>
            <Tabs.Trigger value="demo" className="tab-trigger">
              <GitBranch size={18} />
              <span>Interactive Demo</span>
            </Tabs.Trigger>
            <Tabs.Trigger value="methods" className="tab-trigger">
              <BarChart3 size={18} />
              <span>Methods</span>
            </Tabs.Trigger>
          </Tabs.List>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Tabs.Content value="concept" className="tab-content">
                <section className="section">
                  <h2>What is Mendelian Randomization?</h2>

                  <div className="plain-english">
                    <h3>The Problem: Correlation vs Causation</h3>
                    <p>
                      You've probably heard that <strong>people who drink wine live longer</strong>.
                      But does wine actually cause longer life? Or do wealthier, healthier people just happen
                      to drink more wine? This is the classic <em>correlation vs causation</em> problem.
                    </p>
                    <p>
                      Observational studies can find associations, but they can't prove causation because
                      of <strong>confounders</strong> — other factors (like wealth, education, lifestyle)
                      that affect both the exposure (wine) and the outcome (lifespan).
                    </p>
                  </div>

                  <div className="plain-english">
                    <h3>The Solution: Nature's Randomized Trial</h3>
                    <p>
                      <strong>Mendelian Randomization (MR)</strong> uses a clever trick: your DNA was
                      randomly assigned at conception, like flipping a coin. Some genetic variants make
                      you drink more alcohol, have higher BMI, or lower blood pressure — <em>and you had
                      no choice in the matter</em>.
                    </p>
                    <p>
                      So if people with "high alcohol" genes have different disease rates than people with
                      "low alcohol" genes, we can be more confident that <strong>alcohol actually causes</strong>{' '}
                      the difference — not some hidden confounder.
                    </p>
                  </div>

                  <div className="plain-english">
                    <h3>The Economics Connection: Instrumental Variables</h3>
                    <p>
                      Economists will recognize MR as a form of <strong>instrumental variable (IV) estimation</strong>.
                      The genetic variant is the "instrument" — it affects the outcome only through the exposure,
                      just like how draft lottery numbers affect earnings only through military service.
                    </p>
                    <p>
                      This is why MR has gained traction in economics: it's the same IV logic economists use,
                      but with instruments that are randomly assigned by nature and measured with high precision
                      in large biobank datasets.
                    </p>
                  </div>

                  <div className="key-insight">
                    <Target className="insight-icon" />
                    <div>
                      <h3>Real Example: Does BMI Cause Diabetes?</h3>
                      <p>
                        We know obesity and diabetes are correlated. But does higher BMI actually
                        <em>cause</em> diabetes, or do other factors explain both? MR studies using
                        "obesity genes" have confirmed that <strong>yes, higher BMI causally increases
                        diabetes risk</strong> — supporting weight loss interventions.
                      </p>
                    </div>
                  </div>

                  <MRDiagram />

                  <div className="glossary">
                    <h3>Key Terms Explained</h3>
                    <div className="term-grid">
                      <div className="term">
                        <h4>SNP (Single Nucleotide Polymorphism)</h4>
                        <p>A single letter change in your DNA. Some SNPs affect traits like height, BMI, or blood pressure.</p>
                      </div>
                      <div className="term">
                        <h4>Exposure</h4>
                        <p>The thing we're testing as a potential cause (e.g., BMI, alcohol, blood pressure).</p>
                      </div>
                      <div className="term">
                        <h4>Outcome</h4>
                        <p>The health result we care about (e.g., diabetes, heart disease, lifespan).</p>
                      </div>
                      <div className="term">
                        <h4>Pleiotropy</h4>
                        <p>When a gene affects multiple traits. This can bias results if the gene affects the outcome through paths other than the exposure.</p>
                      </div>
                      <div className="term">
                        <h4>IVW (Inverse Variance Weighted)</h4>
                        <p>The main MR method. Combines evidence from multiple genetic variants, weighting by precision.</p>
                      </div>
                      <div className="term">
                        <h4>MR-Egger</h4>
                        <p>A method that can detect and correct for pleiotropy, but has lower statistical power.</p>
                      </div>
                    </div>
                  </div>

                  <div className="assumptions">
                    <h3>When Does MR Work?</h3>
                    <p className="assumptions-intro">MR requires three assumptions to give valid causal estimates:</p>
                    <div className="assumption-grid">
                      <div className="assumption">
                        <span className="number">1</span>
                        <h4>Relevance</h4>
                        <p>The genetic variants must actually affect the exposure (e.g., "BMI genes" must really change BMI)</p>
                      </div>
                      <div className="assumption">
                        <span className="number">2</span>
                        <h4>Independence</h4>
                        <p>The variants shouldn't be linked to confounders (usually true since DNA is random)</p>
                      </div>
                      <div className="assumption">
                        <span className="number">3</span>
                        <h4>Exclusion</h4>
                        <p>The variants should only affect the outcome through the exposure, not via other pathways (no pleiotropy)</p>
                      </div>
                    </div>
                  </div>

                  <div className="history-section">
                    <div className="section-header">
                      <History className="section-icon" />
                      <h3>History of Mendelian Randomization</h3>
                    </div>
                    <div className="timeline">
                      <div className="timeline-item">
                        <span className="year">1986</span>
                        <div className="timeline-content">
                          <h4>The Birth of MR</h4>
                          <p>
                            Martijn Katan proposed the core idea in a letter to <em>The Lancet</em>. He suggested using
                            genetic variants in the <strong>APOE gene</strong> (which affects cholesterol) to test whether
                            cholesterol truly causes cancer — rather than relying on confounded observational studies.
                          </p>
                        </div>
                      </div>
                      <div className="timeline-item">
                        <span className="year">2003</span>
                        <div className="timeline-content">
                          <h4>The Name is Coined</h4>
                          <p>
                            George Davey Smith and Shah Ebrahim formally named the approach "Mendelian randomization"
                            and laid out its statistical framework, connecting it to Mendel's laws of inheritance
                            and the random assortment of alleles.
                          </p>
                        </div>
                      </div>
                      <div className="timeline-item">
                        <span className="year">2007-2010</span>
                        <div className="timeline-content">
                          <h4>GWAS Revolution</h4>
                          <p>
                            Genome-wide association studies (GWAS) began identifying thousands of genetic variants
                            linked to traits. This gave MR researchers many more "instruments" to work with,
                            dramatically expanding what questions could be answered.
                          </p>
                        </div>
                      </div>
                      <div className="timeline-item">
                        <span className="year">2015+</span>
                        <div className="timeline-content">
                          <h4>Two-Sample MR & Biobanks</h4>
                          <p>
                            Methods for combining GWAS summary statistics enabled "two-sample MR" — using different
                            studies for exposure and outcome. UK Biobank (500,000 participants) and other large
                            cohorts made MR a standard tool in epidemiology.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="landmark-studies">
                    <div className="section-header">
                      <FlaskConical className="section-icon" />
                      <h3>Landmark MR Studies</h3>
                    </div>
                    <p className="intro">
                      These influential studies shaped our understanding of disease causation and informed drug development:
                    </p>
                    <div className="studies-grid">
                      <div className="study-card">
                        <div className="study-finding positive">Causal</div>
                        <h4>LDL Cholesterol → Heart Disease</h4>
                        <p className="study-desc">
                          MR confirmed that LDL cholesterol <strong>causes</strong> coronary heart disease,
                          validating statins as a treatment. Effect sizes matched statin trial results,
                          strengthening confidence in the causal claim.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Supported development of PCSK9 inhibitors and other LDL-lowering drugs.
                        </p>
                        <a href="https://doi.org/10.1001/jama.2017.0972" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                      <div className="study-card">
                        <div className="study-finding positive">Causal</div>
                        <h4>BMI → Type 2 Diabetes</h4>
                        <p className="study-desc">
                          Using hundreds of obesity-related SNPs, MR showed that higher BMI <strong>causally increases</strong>{' '}
                          diabetes risk by ~70% per SD increase in BMI — not just correlation from shared lifestyle factors.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Justified weight-loss interventions and bariatric surgery for diabetes prevention.
                        </p>
                        <a href="https://doi.org/10.1161/CIRCULATIONAHA.116.026560" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                      <div className="study-card">
                        <div className="study-finding negative">Not Causal</div>
                        <h4>HDL Cholesterol → Heart Disease</h4>
                        <p className="study-desc">
                          Despite strong observational correlations, MR found <strong>no causal effect</strong> of
                          HDL ("good cholesterol") on heart disease. Raising HDL doesn't prevent heart attacks.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Explained why HDL-raising drugs (like torcetrapib) failed in clinical trials.
                        </p>
                        <a href="https://doi.org/10.1016/S0140-6736(12)60312-2" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                      <div className="study-card">
                        <div className="study-finding negative">Harmful</div>
                        <h4>Alcohol → Health</h4>
                        <p className="study-desc">
                          MR using <em>ADH1B</em> and <em>ALDH2</em> variants showed that alcohol provides <strong>no
                          cardiovascular benefit</strong> and likely increases blood pressure and stroke risk —
                          overturning the "J-curve" hypothesis.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Changed public health messaging; no "safe" level of alcohol for heart health.
                        </p>
                        <a href="https://doi.org/10.1016/S0140-6736(18)31772-0" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                      <div className="study-card">
                        <div className="study-finding positive">Causal</div>
                        <h4>Education → Health Outcomes</h4>
                        <p className="study-desc">
                          MR found that more years of education <strong>causally reduces</strong> risk of heart disease,
                          diabetes, and depression — beyond just the correlation with socioeconomic status.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Supported education policy as a public health intervention.
                        </p>
                        <a href="https://doi.org/10.1136/bmj.k3016" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                      <div className="study-card">
                        <div className="study-finding positive">Causal</div>
                        <h4>IL-6 → Coronary Heart Disease</h4>
                        <p className="study-desc">
                          MR validated <strong>interleukin-6</strong> as a causal driver of heart disease,
                          supporting anti-inflammatory approaches. The CANTOS trial later confirmed this with
                          an IL-1β inhibitor.
                        </p>
                        <p className="study-impact">
                          <strong>Impact:</strong> Opened a new therapeutic avenue: anti-inflammatory drugs for heart disease.
                        </p>
                        <a href="https://doi.org/10.1016/S0140-6736(12)60110-X" target="_blank" rel="noopener noreferrer" className="study-link">
                          Read paper →
                        </a>
                      </div>
                    </div>
                  </div>
                </section>
              </Tabs.Content>

              <Tabs.Content value="demo" className="tab-content">
                <InteractiveDemo />
              </Tabs.Content>

              <Tabs.Content value="methods" className="tab-content">
                <MethodsComparison />
              </Tabs.Content>
            </motion.div>
          </AnimatePresence>
        </Tabs.Root>
      </main>

      <footer className="footer">
        <p>
          <a href="https://github.com/maxghenis/pymr" target="_blank" rel="noopener">
            GitHub
          </a>
          {' · '}
          <a href="https://maxghenis.github.io/pymr" target="_blank" rel="noopener">
            Documentation
          </a>
          {' · '}
          <code>pip install pymr</code>
        </p>
      </footer>
    </div>
  )
}

export default App
