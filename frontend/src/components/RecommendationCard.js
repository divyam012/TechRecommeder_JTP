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
    const formData = new FormData();
    formData.append("device_type", deviceType);
    formData.append("model", Model);

    const apiUrl = process.env.REACT_APP_API_URL || '';
    const res = await fetch(`${apiUrl}/similar`, { method: "POST", body: formData });
    if (res.ok) {
      const data = await res.json();
      setSimilar(data.recommendations);
    }
    setLoading(false);
  };

  const closeModal = () => {
    setShowSimilar(false);
    setSimilar([]);
  };

  const baseModel = Model && Model.split('(')[0].trim();

  // Render specs for both main and similar cards
  const renderSpecs = (item) => (
    item.deviceType === "laptop" ? (
      <>
        {(item.processor_brand || item.processor_tier) && (
          <div className="spec-item">
            {item.processor_brand ? item.processor_brand : ""}
            {item.processor_tier ? ` ${item.processor_tier}` : ""}
            {item.processor_gen ? ` Gen ${item.processor_gen}` : ""}
          </div>
        )}
        {(item.RAM || item.Storage) && (
          <div className="spec-item">
            {item.RAM ? `${item.RAM}GB` : ""}{item.Storage ? ` / ${item.Storage}GB` : ""}{item.Primary_Storage_Type ? ` ${item.Primary_Storage_Type}`.toUpperCase() : ""}
          </div>
        )}
        {item.display_size && <div className="spec-item">{item.display_size}″</div>}
      </>
    ) : (
      <>
        {(item.RAM || item.Storage) && (
          <div className="spec-item">
            {item.RAM ? `${item.RAM}GB` : ""}{item.Storage ? ` / ${item.Storage}GB` : ""}
          </div>
        )}
        {item.Battery && <div className="spec-item">{item.Battery} mAh</div>}
        {item.Rear_cam_mp && <div className="spec-item">{item.Rear_cam_mp}MP{item.Num_rear_cam ? ` (${item.Num_rear_cam} cameras)` : ""}</div>}
        {item.Front_cam_mp && <div className="spec-item">Front {item.Front_cam_mp}MP</div>}
        {item.display_size && <div className="spec-item">{item.display_size}″</div>}
        {item.fiveg !== undefined && item.fiveg !== null && item.fiveg && <div className="spec-item">5G</div>}
      </>
    )
  );

  return (
    <div className="recommendation-card">
      <div className="card-header">
        <div className="brand">{Brand}</div>
        <div className="model">{baseModel}</div>
      </div>
      <div className="spec-grid">
        {renderSpecs(props)}
      </div>
      <div className="price-section">
        <span className="price">₹{Number(Price).toLocaleString('en-IN')}</span>
      </div>
      <button className="similar-btn" onClick={fetchSimilar}>
        {loading ? "Loading..." : "Show Similar Items"}
      </button>
      {showSimilar && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>×</button>
            <h4>Similar Items:</h4>
            <div className="similar-cards">
              {similar.length === 0 && loading && <div>Loading...</div>}
              {similar.length === 0 && !loading && <div>No similar items found.</div>}
              {similar.map((item, idx) => (
                <div key={idx} className="recommendation-card">
                  <div className="card-header">
                    <div className="brand">{item.Brand}</div>
                    <div className="model">{item.Model && item.Model.split('(')[0].trim()}</div>
                  </div>
                  <div className="spec-grid">
                    {renderSpecs({ ...item, deviceType })}
                  </div>
                  <div className="price-section">
                    <span className="price">₹{Number(item.Price).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;