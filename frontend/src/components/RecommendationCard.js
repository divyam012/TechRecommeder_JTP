import React, { useState } from "react";

// Card for a single recommendation (laptop or phone)
const RecommendationCard = (props) => {
  const { Brand, Model, Price, deviceType } = props;

  const [similar, setSimilar] = useState([]);
  const [showSimilar, setShowSimilar] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch similar items from backend
  const fetchSimilar = async () => {
    setLoading(true);
    setShowSimilar(true);
    setSimilar([]);
    
    // Validate model exists
    if (!Model) {
      setLoading(false);
      return;
    }
    
    const formData = new FormData();
    formData.append("device_type", deviceType);
    formData.append("model", Model);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const res = await fetch(`${apiUrl}/similar`, { 
        method: "POST", 
        body: formData 
      });
      
      if (res.ok) {
        const data = await res.json();
        // Ensure recommendations is always an array
        setSimilar(Array.isArray(data?.recommendations) ? data.recommendations : []);
      }
    } catch (error) {
      console.error("Error fetching similar items:", error);
      setSimilar([]);
    } finally {
      setLoading(false);
    }
  };

  const closeModal = () => {
    setShowSimilar(false);
    setSimilar([]);
  };

  // Safely handle model names
  const baseModel = Model ? Model.split('(')[0].trim() : "Unknown Model";

  // Render specs for both main and similar cards
  const renderSpecs = (item) => {
    // Add safety checks for all properties
    const safeItem = item || {};
    
    return deviceType === "laptop" ? (
      <>
        {(safeItem.processor_brand || safeItem.processor_tier) && (
          <div className="spec-item">
            {safeItem.processor_brand || ""}
            {safeItem.processor_tier ? ` ${safeItem.processor_tier}` : ""}
            {safeItem.processor_gen ? ` Gen ${safeItem.processor_gen}` : ""}
          </div>
        )}
        {(safeItem.RAM || safeItem.Storage) && (
          <div className="spec-item">
            {safeItem.RAM ? `${safeItem.RAM}GB` : ""}
            {safeItem.Storage ? ` / ${safeItem.Storage}GB` : ""}
            {safeItem.Primary_Storage_Type ? ` ${safeItem.Primary_Storage_Type.toUpperCase()}` : ""}
          </div>
        )}
        {safeItem.display_size && <div className="spec-item">{safeItem.display_size}″</div>}
      </>
    ) : (
      <>
        {(safeItem.RAM || safeItem.Storage) && (
          <div className="spec-item">
            {safeItem.RAM ? `${safeItem.RAM}GB` : ""}
            {safeItem.Storage ? ` / ${safeItem.Storage}GB` : ""}
          </div>
        )}
        {safeItem.Battery && <div className="spec-item">{safeItem.Battery} mAh</div>}
        {safeItem.Rear_cam_mp && (
          <div className="spec-item">
            {safeItem.Rear_cam_mp}MP
            {safeItem.Num_rear_cam ? ` (${safeItem.Num_rear_cam} cameras)` : ""}
          </div>
        )}
        {safeItem.Front_cam_mp && <div className="spec-item">Front {safeItem.Front_cam_mp}MP</div>}
        {safeItem.display_size && <div className="spec-item">{safeItem.display_size}″</div>}
        {safeItem.fiveg && <div className="spec-item">5G</div>}
      </>
    );
  };

  return (
    <div className="recommendation-card">
      <div className="card-header">
        <div className="brand">{Brand || "Unknown Brand"}</div>
        <div className="model">{baseModel}</div>
      </div>
      <div className="spec-grid">
        {renderSpecs(props)}
      </div>
      <div className="price-section">
        <span className="price">
          ₹{Price ? Number(Price).toLocaleString('en-IN') : "N/A"}
        </span>
      </div>
      <button 
        className="similar-btn" 
        onClick={fetchSimilar}
        disabled={!Model}  // Disable if no model
      >
        {loading ? "Loading..." : "Show Similar Items"}
      </button>
      
      {showSimilar && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>×</button>
            <h4>Similar Items:</h4>
            <div className="similar-cards">
              {loading && <div>Loading...</div>}
              
              {!loading && similar.length === 0 && (
                <div>No similar items found.</div>
              )}
              
              {!loading && similar.length > 0 && similar.map((item, idx) => {
                // Safe model name handling
                const similarModel = item?.Model 
                  ? item.Model.split('(')[0].trim() 
                  : "Unknown Model";
                  
                return (
                  <div key={`${item?.Brand || idx}-${item?.Model || idx}`} className="recommendation-card">
                    <div className="card-header">
                      <div className="brand">{item?.Brand || "Unknown Brand"}</div>
                      <div className="model">{similarModel}</div>
                    </div>
                    <div className="spec-grid">
                      {renderSpecs({ ...item, deviceType })}
                    </div>
                    <div className="price-section">
                      <span className="price">
                        ₹{item?.Price ? Number(item.Price).toLocaleString('en-IN') : "N/A"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;