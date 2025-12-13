import { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:8000";

interface Image {
  id: number;
  url: string;
  likes: number;
  dislikes: number;
}

interface UseAppRequestsReturn {
  images: Image[];
  loading: boolean;
  error: string | null;
  handleVote: (imageId: number, voteType: string) => Promise<void>;
  handleExport: () => Promise<void>;
}

export const useAppRequests = (): UseAppRequestsReturn => {
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_URL}/images`);
      if (!response.ok) throw new Error("Failed to fetch images");
      const data: Image[] = await response.json();
      setImages(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setLoading(false);
    }
  };

  // eslint-disable-next-line max-len
  const handleVote = useCallback(async (
    imageId: number,
    voteType: string
  ): Promise<void> => {
    setImages((prevImages) =>
      prevImages.map((img) => {
        if (img.id === imageId) {
          let newLikes = img.likes;
          let newDislikes = img.dislikes;

          if (voteType === "like") newLikes++;
          else if (voteType === "dislike") newDislikes++;

          return {
            ...img,
            likes: newLikes,
            dislikes: newDislikes,
          };
        }
        return img;
      })
    );

    try {
      const response = await fetch(`${API_URL}/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_id: imageId, vote_type: voteType }),
      });

      if (!response.ok) throw new Error("Failed to vote");
    } catch (err) {
      // Revert on error - fetch current state from server
      fetchImages();
      setError("Failed to submit vote");

      setTimeout(() => setError(null), 3000);

      // eslint-disable-next-line no-console
      console.error("Vote error:", err);
    }
  }, []);

  const handleExport = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_URL}/export-votes`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "votes.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Export error:", err);
    }
  };

  return {
    images,
    loading,
    error,
    handleVote,
    handleExport,
  };
};
