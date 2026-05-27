// Frontend component generator for correlation explorer
import fs from 'fs/promises';
import path from 'path';

const DATA_PATH = path.join(process.cwd(), 'public', 'data', 'correlations.json');
const OUTPUT_PATH = path.join(process.cwd(), 'src', 'components', 'CorrelationExplorer.jsx');

const COMPONENT_TEMPLATE = `// Auto-generated correlation explorer component
import React from 'react';
import { useCurrentIndicator } from '../hooks/useDashboard';

export default function CorrelationExplorer() {
  const { currentIndicator } = useCurrentIndicator();
  const correlations = require('../data/correlations.json').indicators[currentIndicator] || {};

  return (
    <div className="correlation-panel">
      <h3>Related Indicators</h3>
      
      {correlations.positive?.length > 0 && (
        <div className="correlation-group positive">
          <h4>Positively Correlated</h4>
          <ul>
            {correlations.positive.map((item) => (
              <li key={item.indicator}>
                <button 
                  onClick={() => setIndicator(item.indicator)}
                  title={"r = " + item.value.toFixed(3)}
                >
                  {item.indicator}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {correlations.negative?.length > 0 && (
        <div className="correlation-group negative">
          <h4>Negatively Correlated</h4>
          <ul>
            {correlations.negative.map((item) => (
              <li key={item.indicator}>
                <button 
                  onClick={() => setIndicator(item.indicator)}
                  title={"r = " + item.value.toFixed(3)}
                >
                  {item.indicator}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!correlations.positive && !correlations.negative && (
        <p>No significant correlations found for this indicator</p>
      )}
    </div>
  );
}
`;

async function main() {
  try {
    // Verify correlations data exists
    await fs.access(DATA_PATH);
    
    // Create components directory if needed
    await fs.mkdir(path.dirname(OUTPUT_PATH), { recursive: true });
    
    // Write component file
    await fs.writeFile(OUTPUT_PATH, COMPONENT_TEMPLATE);
    
    console.log(`Successfully created: ${OUTPUT_PATH}`);
    console.log('Component ready for integration into the dashboard');
  } catch (err) {
    console.error('Component generation failed:', err);
    process.exit(1);
  }
}

main();