
import { useEffect, useMemo, useState } from "react";
import { LogOut, UploadCloud, Sparkles, Trash2 } from "lucide-react";
import { api, imageUrl } from "../api";

const categories = [
  { key: "tops", label: "Tops", emoji: "👕" },
  { key: "bottoms", label: "Bottoms", emoji: "👖" },
  { key: "shoes", label: "Shoes", emoji: "👟" },
];

function readableGender(gender) {
  const map = {
    men: "Men",
    women: "Women",
    unisex: "Unisex",
    unknown: "Unknown",
  };

  return map[gender] || gender || "Unknown";
}

function readableSeason(season) {
  const map = {
    spring: "Spring",
    summer: "Summer",
    fall: "Fall",
    winter: "Winter",
    unknown: "Unknown",
  };

  return map[season] || season || "Unknown";
}

function readableWeatherGroup(group) {
  const map = {
    hot: "Hot weather",
    cold: "Cold weather",
    all_season: "All season",
    unknown: "Unknown",
  };

  return map[group] || group || "Unknown";
}

function formatConfidence(value) {
  if (value === undefined || value === null) {
    return "0.0";
  }

  return (value * 100).toFixed(1);
}

export default function WardrobePage({ user, onLogout }) {
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const grouped = useMemo(() => {
    return categories.reduce((acc, cat) => {
      acc[cat.key] = items.filter((item) => item.category === cat.key);
      return acc;
    }, {});
  }, [items]);

  const fetchItems = async () => {
    const response = await api.get("/items");
    setItems(response.data);
  };

  useEffect(() => {
    fetchItems().catch(() => setMessage("Không tải được tủ đồ."));
  }, []);

  const handleFile = (event) => {
    const selected = event.target.files?.[0];

    setFile(selected || null);
    setPreview(selected ? URL.createObjectURL(selected) : "");
  };

  const upload = async (event) => {
    event.preventDefault();

    if (!file) {
      setMessage("Bạn cần chọn một ảnh trước.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const formData = new FormData();

      formData.append("name", name);
      formData.append("image", file);

      const response = await api.post("/items", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setItems((prev) => [response.data, ...prev]);
      setName("");
      setFile(null);
      setPreview("");

      setMessage(
        `Item saved in ${response.data.category_name || response.data.category}. AI predicts: ${readableGender(
          response.data.gender
        )} · ${readableSeason(response.data.season)} · ${readableWeatherGroup(
          response.data.weather_group
        )}.`
      );
    } catch (err) {
      setMessage(err.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (id) => {
    await api.delete(`/items/${id}`);
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <main className="wardrobe-page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Welcome, {user.name}</p>
          <h1>My Smart Wardrobe</h1>
        </div>

        <button className="ghost-btn" onClick={onLogout}>
          <LogOut size={18} /> Logout
        </button>
      </header>

      <section className="hero-grid">
        <form className="upload-panel" onSubmit={upload}>
          <div className="section-title">
            <UploadCloud />

            <div>
              <h2>Upload clothing image</h2>
              <p>
                AI will automatically classify item type, gender, season, and
                weather group.
              </p>
            </div>
          </div>

          <label>
            Item name
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Example: White shirt"
            />
          </label>

          <p className="note">
            AI sẽ tự phân loại item vào Tops / Bottoms / Shoes.
          </p>

          <label className="file-box">
            {preview ? (
              <img src={preview} alt="Preview" />
            ) : (
              <span>Click to choose image</span>
            )}

            <input type="file" accept="image/*" onChange={handleFile} />
          </label>

          {message && <p className="message">{message}</p>}

          <button className="primary-btn" disabled={loading}>
            {loading ? "Classifying..." : "Classify & Save"}
          </button>
        </form>

        <aside className="ai-info-card">
          <Sparkles size={34} />

          <h2>Model output</h2>

          <p>Website hiện dùng 2 model AI:</p>

          <div className="label-pills">
            <span>tops</span>
            <span>bottoms</span>
            <span>shoes</span>
            <span>men</span>
            <span>women</span>
            <span>unisex</span>
            <span>spring</span>
            <span>summer</span>
            <span>fall</span>
            <span>winter</span>
          </div>

          <p className="note">
            Model 1 tự phân loại item vào Tops / Bottoms / Shoes. Model 2 dự
            đoán gender và season. Sau đó web map season thành hot / cold /
            all season.
          </p>
        </aside>
      </section>

      <section className="closet">
        {categories.map((cat) => (
          <div className="closet-column" key={cat.key}>
            <h2>
              {cat.emoji} {cat.label}
            </h2>

            <div className="items-list">
              {(grouped[cat.key] || []).length === 0 && (
                <p className="empty">No items</p>
              )}

              {(grouped[cat.key] || []).map((item) => (
                <article className="item-card" key={item.id}>
                  <img
                    src={imageUrl(item.image_url)}
                    alt={item.name || item.category_name || item.category}
                  />

                  <div className="item-body">
                    <h3>{item.name || "Unnamed item"}</h3>

                    <p>
                      {readableGender(item.gender)} ·{" "}
                      {readableSeason(item.season)} ·{" "}
                      {readableWeatherGroup(item.weather_group)}
                    </p>

                    <small>
                      Item: {formatConfidence(item.item_confidence)}% · Gender:{" "}
                      {formatConfidence(item.gender_confidence)}% · Season:{" "}
                      {formatConfidence(item.season_confidence)}%
                    </small>
                  </div>

                  <button
                    className="delete-btn"
                    onClick={() => removeItem(item.id)}
                    aria-label="Delete item"
                  >
                    <Trash2 size={16} />
                  </button>
                </article>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  );
}

