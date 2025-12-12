import { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await fetch(`${API_URL}/images`);
      if (!response.ok) throw new Error('Failed to fetch images');
      const data = await response.json();
      setImages(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleVote = async (imageId, voteType) => {
    try {
      const response = await fetch(`${API_URL}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_id: imageId, vote_type: voteType }),
      });
      
      if (!response.ok) throw new Error('Failed to vote');
      
      // Refresh images to get updated counts
      fetchImages();
    } catch (err) {
      console.error('Vote error:', err);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch(`${API_URL}/export`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'votes.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  if (loading) return <div className="loading">Loading images...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="App">
      <header className="header">
        <h1>PicsFeed - Vote on Random Pictures</h1>
        <button onClick={handleExport} className="export-btn">
          Export Votes to CSV
        </button>
      </header>
      
      <div className="image-grid">
        {images.map((image) => (
          <div key={image.id} className="image-card">
            <img src={image.url} alt={`Image ${image.id}`} loading="lazy" />
            <div className="vote-section">
              <button 
                onClick={() => handleVote(image.id, 'like')}
                className="vote-btn like-btn"
              >
                👍 {image.likes}
              </button>
              <button 
                onClick={() => handleVote(image.id, 'dislike')}
                className="vote-btn dislike-btn"
              >
                👎 {image.dislikes}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
