import React, { useState, useEffect, useCallback } from "react";
import "./styles.css";
import RecommendationCard from "./components/RecommendationCard";

// Main App component
function App() {
  // State for form and recommendations
  const [deviceType, setDeviceType] = useState("");
  const [usageType, setUsageType] = useState("");
  const [budget, setBudget] = useState("");
  const [recommendations20, setRecommendations20] = useState([]);
  const [shownIndices, setShownIndices] = useState(new Set());
  const [currentFive, setCurrentFive] = useState([]);
  const [error, setError] = useState("");

  // Usage options for each device type
  const USAGE_OPTIONS = {
    laptop: ["gaming", "business", "basic", "student"],
    phone: ["gaming", "camera", "business", "basic"],
  };

  // Helper to pick 5 new recommendations that haven't been shown yet
  const pickFiveNew = useCallback(
    (shown) => {
      if (!recommendations20.length) return { picked: [], newShown: shown };
      // Find indices not yet shown
      let available = recommendations20
        .map((_, idx) => idx)
        .filter((i) => !shown.has(i));
      let pool = available,
        newShown = new Set(shown);
      // If less than 5 left, reset pool
      if (available.length < 5) {
        newShown = new Set();
        pool = recommendations20.map((_, idx) => idx);
      }
      // Randomly pick 5
      const picked = [];
      while (picked.length < 5 && pool.length) {
        const randomIdx = Math.floor(Math.random() * pool.length);
        picked.push(pool[randomIdx]);
        pool.splice(randomIdx, 1);
      }
      picked.forEach((i) => newShown.add(i));
      return { picked: picked.map((i) => recommendations20[i]), newShown };
    },
    [recommendations20]
  );

  // Fetch recommendations from backend
  async function fetchRecommendations() {
    setError("");
    if (!budget || isNaN(budget) || budget <= 0) {
      setError("Please enter a valid budget.");
      return;
    }
    const formData = new FormData();
    formData.append("device_type", deviceType);
    formData.append("budget", budget);
    formData.append("usage_type", usageType);

    try {
      const response = await fetch("/recommend", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        setError(errData.error || "Error fetching recommendations");
        return;
      }
      const data = await response.json();
      setRecommendations20(data.recommendations);
      setShownIndices(new Set());
    } catch {
      setError("Network error");
    }
  }

  // Handle Recommend button
  function onRecommend() {
    fetchRecommendations();
  }

  // Handle Refresh button
  function onRefresh() {
    if (!recommendations20.length) {
      setError("No recommendations to refresh. Please click Recommend first.");
      return;
    }
    const { picked, newShown } = pickFiveNew(shownIndices);
    setCurrentFive(picked);
    setShownIndices(newShown);
  }

  // When recommendations change, show a fresh set of 5
  useEffect(() => {
    if (recommendations20.length) {
      const { picked, newShown } = pickFiveNew(new Set());
      setCurrentFive(picked);
      setShownIndices(newShown);
    } else {
      setCurrentFive([]);
      setShownIndices(new Set());
    }
  }, [recommendations20, pickFiveNew]);

  return (
    <div className="app-container">
      <header>
        <h1>Tech Product Recommendation System</h1>
        <p>
          Get smart recommendations for laptops and phones based on your needs and
          budget.
        </p>
      </header>

      {/* Device and usage selection form */}
      <form className="device-form" onSubmit={(e) => e.preventDefault()}>
        <div className="form-row">
          <div className="form-group compact">
            <label>Device</label>
            <select
              value={deviceType}
              onChange={(e) => {
                setDeviceType(e.target.value);
                setUsageType(""); // Reset usage when device changes
              }}
            >
              <option value="">--Select--</option>
              <option value="laptop">Laptop</option>
              <option value="phone">Phone</option>
            </select>
          </div>
          <div className="form-group compact">
            <label>Usage</label>
            <select
              value={usageType}
              onChange={(e) => setUsageType(e.target.value)}
              disabled={!deviceType}
            >
              <option value="">--Select--</option>
              {deviceType &&
                USAGE_OPTIONS[deviceType].map((usage) => (
                  <option key={usage} value={usage}>
                    {usage.charAt(0).toUpperCase() + usage.slice(1)}
                  </option>
                ))}
            </select>
          </div>
          <div className="form-group compact">
            <label>Budget (₹)</label>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="INR"
              min="1000"
              step="1000"
            />
          </div>
          <div className="button-group compact">
            <button
              type="button"
              className="recommend-btn"
              onClick={onRecommend}
              disabled={!deviceType || !usageType}
            >
              Recommend
            </button>
            <button type="button" className="refresh-btn" onClick={onRefresh}>
              Refresh
            </button>
          </div>
        </div>
      </form>

      {error && <div className="error">{error}</div>}

      {/* Show recommendations */}
      <div className="recommendations-row">
        {currentFive.length > 0 && <h2>Top Recommendations:</h2>}
        <div className="recommendations-flex">
          {currentFive.map((rec, idx) => (
            <RecommendationCard
              key={`${rec.Brand}-${rec.Model}-${idx}`}
              {...rec}
              deviceType={deviceType}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
