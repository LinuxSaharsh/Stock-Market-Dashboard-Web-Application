import React, { useState } from 'react';
import './App.css';
import StockChart from "./StockChart";
// Main App component


function App() {
  // Sidebar open/close state
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Selected company state
  const [selectedCompany, setSelectedCompany] = useState(null);

  // Buy price input state
  const [buyPrice, setBuyPrice] = useState('');

  // Mock current prices for companies
  const mockPrices = {
    RELIANCE: 2800,
    TCS: 3900,
    INFY: 1600,
    HDFCBANK: 1700,
    ICICIBANK: 1100,
    SBIN: 600,
    BAJFINANCE: 7000,
    LT: 3500,
    ITC: 450,
    BHARTIARTL: 1200,
    AAPL: 195,
    MSFT: 410,
    AMZN: 175,
    GOOGL: 130,
    TSLA: 250,
  };

  // Toggle sidebar open/close
  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Company list data
  const indianCompanies = [
    { name: 'Reliance Industries Ltd', symbol: 'RELIANCE' },
    { name: 'Tata Consultancy Services', symbol: 'TCS' },
    { name: 'Infosys Ltd', symbol: 'INFY' },
    { name: 'HDFC Bank Ltd', symbol: 'HDFCBANK' },
    { name: 'ICICI Bank Ltd', symbol: 'ICICIBANK' },
    { name: 'State Bank of India', symbol: 'SBIN' },
    { name: 'Bajaj Finance Ltd', symbol: 'BAJFINANCE' },
    { name: 'Larsen & Toubro Ltd', symbol: 'LT' },
    { name: 'ITC Ltd', symbol: 'ITC' },
    { name: 'Bharti Airtel Ltd', symbol: 'BHARTIARTL' },
  ];
  const usCompanies = [
    { name: 'Apple Inc', symbol: 'AAPL' },
    { name: 'Microsoft Corp', symbol: 'MSFT' },
    { name: 'Amazon.com Inc', symbol: 'AMZN' },
    { name: 'Alphabet Inc', symbol: 'GOOGL' },
    { name: 'Tesla Inc', symbol: 'TSLA' },
  ];

  // Handle company selection
  const handleCompanySelect = (company) => {
    setSelectedCompany(company);
    setBuyPrice(''); // Reset buy price on new selection
  };

  // Calculate profit/loss
  let profitLoss = null;
  if (selectedCompany && buyPrice !== '') {
    const currentPrice = mockPrices[selectedCompany.symbol];
    profitLoss = currentPrice - parseFloat(buyPrice);
  }

  return (
    <div className="dashboard-container" style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar: Expandable/Collapsible Company List */}
      <div
        className="company-list"
        style={{
          width: sidebarOpen ? '250px' : '60px', // Change width when collapsed
          background: '#f5f5f5',
          overflowY: 'auto',
          padding: sidebarOpen ? '1rem' : '0.5rem',
          transition: 'width 0.3s',
          position: 'relative',
          minWidth: '60px', // Prevent sidebar from disappearing
          boxSizing: 'border-box',
        }}
      >
        {/* Toggle Button - always visible on left edge */}
        <button
          onClick={handleSidebarToggle}
          style={{
            position: 'absolute',
            top: '10px',
            left: sidebarOpen ? '230px' : '40px', // Position at edge of sidebar
            width: '20px',
            height: '40px',
            background: '#ccc',
            border: 'none',
            borderRadius: '0 5px 5px 0',
            cursor: 'pointer',
            zIndex: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
          }}
          title={sidebarOpen ? 'Collapse' : 'Expand'}
        >
          {sidebarOpen ? '<' : '>'}
        </button>

        {/* Company List Content (hidden when collapsed) */}
        {sidebarOpen ? (
          <>
            {/* Indian Companies */}
            <h2 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Indian Companies (NSE/BSE)</h2>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {indianCompanies.map((company) => (
                <li
                  key={company.symbol}
                  style={{ marginBottom: '0.5rem', cursor: 'pointer', fontWeight: selectedCompany && selectedCompany.symbol === company.symbol ? 'bold' : 'normal', color: selectedCompany && selectedCompany.symbol === company.symbol ? '#1976d2' : 'inherit' }}
                  onClick={() => handleCompanySelect(company)}
                  title={`Select ${company.name}`}
                >
                  {company.name} <span style={{ color: '#888' }}>({company.symbol})</span>
                </li>
              ))}
            </ul>
            {/* US Companies */}
            <h2 style={{ fontSize: '1rem', margin: '1rem 0 0.5rem 0' }}>US Companies (NASDAQ/NYSE)</h2>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {usCompanies.map((company) => (
                <li
                  key={company.symbol}
                  style={{ marginBottom: '0.5rem', cursor: 'pointer', fontWeight: selectedCompany && selectedCompany.symbol === company.symbol ? 'bold' : 'normal', color: selectedCompany && selectedCompany.symbol === company.symbol ? '#1976d2' : 'inherit' }}
                  onClick={() => handleCompanySelect(company)}
                  title={`Select ${company.name}`}
                >
                  {company.name} <span style={{ color: '#888' }}>({company.symbol})</span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          // Collapsed: show only an icon or minimal content
          <div style={{ textAlign: 'center', marginTop: '2rem', color: '#888', fontSize: '0.8rem' }}>
            <span>☰</span>
          </div>
        )}
      </div>

      {/* Main Panel: Chart Area */}
      <div className="chart-area" style={{ flex: 1, background: '#fff', padding: '2rem' }}>
        {/* Chart area header */}
        <h2>Stock Dashboard</h2>
        {/* Show selected company info and buy/profit/loss calculation */}
        {selectedCompany ? (
          <div style={{ maxWidth: '400px', margin: '0 auto', padding: '1rem', border: '1px solid #eee', borderRadius: '8px', background: '#fafafa' }}>
            <h3>{selectedCompany.name} <span style={{ color: '#888' }}>({selectedCompany.symbol})</span></h3>
            <p>Current Price: <strong>₹{mockPrices[selectedCompany.symbol]}</strong></p>
            <label htmlFor="buyPrice">Your Buy Price:</label>
            <input
              id="buyPrice"
              type="number"
              value={buyPrice}
              onChange={e => setBuyPrice(e.target.value)}
              style={{ marginLeft: '0.5rem', padding: '0.25rem', borderRadius: '4px', border: '1px solid #ccc', width: '100px' }}
              placeholder="Enter price"
            />

            {profitLoss !== null && (
              <p style={{ marginTop: '1rem', fontWeight: 'bold', color: profitLoss > 0 ? 'green' : profitLoss < 0 ? 'red' : 'black' }}>
                {profitLoss > 0 ? 'Profit' : profitLoss < 0 ? 'Loss' : 'No Change'}: ₹{Math.abs(profitLoss).toFixed(2)}
              </p>
            )}
            
          </div>
        ) : (
          <div style={{ height: '400px', border: '1px dashed #ccc', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
            Select a company from the sidebar to view details.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
