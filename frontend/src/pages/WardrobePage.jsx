import { useEffect, useMemo, useState } from "react";
import { LogOut, UploadCloud, Sparkles, Trash2 } from "lucide-react";
import { api, imageUrl } from "../api";

const categories = [
  { key: "tops", label: "Tops", emoji: "👕" },
  { key: "bottoms", label: "Bottoms", emoji: "👖" },
  { key: "shoes", label: "Shoes", emoji: "👟" },
  { key: "accessories", label: "Accessories", emoji: "👜" },
];

function readableLabel(label) {
  const map = {
    men_hot: "male -hot weather",
    men_cold: "male -cold weather",
    woman_hot: "female -hot weather",
    woman_cold: "female -cold weather",
    women_hot: "women -hot weather",
    women_cold: "women -cold weather",
    model_not_loaded: "Model not loaded",
  };
  return map[label] || label;
}

export default function WardrobePage({ user, onLogout }) {
  const [items, setItems] = useState([]);
  const [category, setCategory] = useState("tops");
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
      formData.append("category", category);
      formData.append("name", name);
      formData.append("image", file);
      const response = await api.post("/items", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setItems((prev) => [response.data, ...prev]);
      setName("");
      setFile(null);
      setPreview("");
      setMessage(`Item saved. AI classification: ${readableLabel(response.data.ai_label)}.`);
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
        <button className="ghost-btn" onClick={onLogout}><LogOut size={18} /> Logout</button>
      </header>

      <section className="hero-grid">
        <form className="upload-panel" onSubmit={upload}>
          <div className="section-title">
            <UploadCloud />
            <div>
              <h2>Upload clothing image</h2>
              <p>AI model predicts hot/cold + gender. You choose the closet section.</p>
            </div>
          </div>

          <label>
            Item name
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Example: White shirt" />
          </label>

          <label>
            Closet category
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              {categories.map((cat) => <option key={cat.key} value={cat.key}>{cat.label}</option>)}
            </select>
          </label>

          <label className="file-box">
            {preview ? <img src={preview} alt="Preview" /> : <span>Click to choose image</span>}
            <input type="file" accept="image/*" onChange={handleFile} />
          </label>

          {message && <p className="message">{message}</p>}
          <button className="primary-btn" disabled={loading}>{loading ? "Classifying..." : "Classify & Save"}</button>
        </form>

        <aside className="ai-info-card">
          <Sparkles size={34} />
          <h2>Model output</h2>
          <p>Your current model supports only these AI labels:</p>
          <div className="label-pills">
            <span>men_hot</span><span>men_cold</span><span>women_hot</span><span>women_cold</span>
          </div>
          <p className="note">Because the model cannot detect “shirt/pants/shoes/accessories”, the website saves the closet category from your manual selection.</p>
        </aside>
      </section>

      <section className="closet">
        {categories.map((cat) => (
          <div className="closet-column" key={cat.key}>
            <h2>{cat.emoji} {cat.label}</h2>
            <div className="items-list">
              {(grouped[cat.key] || []).length === 0 && <p className="empty">No items</p>}
              {(grouped[cat.key] || []).map((item) => (
                <article className="item-card" key={item.id}>
                  <img src={imageUrl(item.image_url)} alt={item.name || item.category_name} />
                  <div className="item-body">
                    <h3>{item.name || "Unnamed item"}</h3>
                    <p>{readableLabel(item.ai_label)}</p>
                    <small>Confidence: {(item.ai_confidence * 100).toFixed(1)}%</small>
                  </div>
                  <button className="delete-btn" onClick={() => removeItem(item.id)} aria-label="Delete item"><Trash2 size={16} /></button>
                </article>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  );
}
