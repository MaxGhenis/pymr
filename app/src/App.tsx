import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import * as Tabs from '@radix-ui/react-tabs'
import { Dna, GitBranch, Target, BarChart3, Code, BookOpen } from 'lucide-react'
import { MRDiagram } from './components/MRDiagram'
import { InteractiveDemo } from './components/InteractiveDemo'
import { MethodsComparison } from './components/MethodsComparison'
import { CodeExamples } from './components/CodeExamples'
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
            <Tabs.Trigger value="code" className="tab-trigger">
              <Code size={18} />
              <span>Code Examples</span>
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
                  <p className="intro">
                    Mendelian Randomization (MR) is a method that uses genetic variants as
                    <strong> natural experiments</strong> to estimate causal effects of
                    exposures on outcomes.
                  </p>

                  <div className="key-insight">
                    <Target className="insight-icon" />
                    <div>
                      <h3>The Key Insight</h3>
                      <p>
                        Because genetic variants are assigned at conception (like a randomized trial),
                        they're not affected by confounding factors that plague observational studies.
                      </p>
                    </div>
                  </div>

                  <MRDiagram />

                  <div className="assumptions">
                    <h3>Core Assumptions</h3>
                    <div className="assumption-grid">
                      <div className="assumption">
                        <span className="number">1</span>
                        <h4>Relevance</h4>
                        <p>The genetic variant is associated with the exposure</p>
                      </div>
                      <div className="assumption">
                        <span className="number">2</span>
                        <h4>Independence</h4>
                        <p>No confounders between the variant and outcome</p>
                      </div>
                      <div className="assumption">
                        <span className="number">3</span>
                        <h4>Exclusion</h4>
                        <p>The variant only affects outcome through the exposure</p>
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

              <Tabs.Content value="code" className="tab-content">
                <CodeExamples />
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
