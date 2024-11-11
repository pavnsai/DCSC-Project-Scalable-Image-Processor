import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; // Import useParams from react-router-dom
import './ImageGallery.css';

const DownloadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

const ExpandIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 3h6v6M14 10l7-7M9 21H3v-6M10 14l-7 7" />
  </svg>
);

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);


const ImageGallery = () => {
  const { UUID: urlUUID } = useParams(); // Get the UUID from the URL params
  const [uuid, setUuid] = useState(urlUUID || ''); // Use URL UUID or fallback to empty
  const [images, setImages] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (urlUUID) {
      fetchImages(urlUUID);
    }
  }, [urlUUID]);

  const fetchImages = async (uuidToFetch) => {
    try {
      const response = await fetch(`http://localhost:8080/get-processed-images?UUID=${uuidToFetch}`);
      const data = await response.json();
      setImages(data.output_urls || []);
    } catch (error) {
      console.error('Error fetching images:', error);
      alert('Failed to fetch images. Please try again.');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (uuid) fetchImages(uuid);
  };

  const handlePopup = (image) => {
    setSelectedImage(image);
    setShowPopup(true);
  };

  const downloadImage = async (url, fileName) => {
    try {
      setIsDownloading(true);

      const response = await fetch(url);
      const blob = await response.blob();

      const blobUrl = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName || 'image.jpg';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Error downloading image:', error);
      alert('Failed to download image. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="gallery-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={uuid}
            onChange={(e) => setUuid(e.target.value)}
            placeholder="Enter UUID"
            className="uuid-input"
          />
          <button type="submit" className="fetch-button">
            Fetch Images
          </button>
        </div>
      </form>

      <div className="image-grid">
        {images.map((image, index) => (
          <div key={index} className="image-card">
            <div className="image-wrapper">
              <img
                src={image.url}
                alt={`Image ${index}`}
                className="gallery-image"
              />
              <div className="image-overlay">
                <button
                  onClick={() => handlePopup(image)}
                  className="action-button"
                  title="View Image"
                >
                  <ExpandIcon />
                </button>
                <button
                  onClick={() => downloadImage(image.url, image.file_name)}
                  className="action-button"
                  disabled={isDownloading}
                  title="Download Image"
                >
                  {isDownloading ? (
                    <span className="loading-spinner"></span>
                  ) : (
                    <DownloadIcon />
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showPopup && (
        <div className="modal-overlay" onClick={(e) => {
          if (e.target === e.currentTarget) setShowPopup(false);
        }}>
          <div className="modal-content">
            <div className="modal-actions">
              <button
                onClick={() => downloadImage(selectedImage.url, selectedImage.file_name)}
                className="modal-button"
                disabled={isDownloading}
                title="Download Image"
              >
                {isDownloading ? (
                  <span className="loading-spinner"></span>
                ) : (
                  <DownloadIcon />
                )}
              </button>
              <button
                onClick={() => setShowPopup(false)}
                className="modal-button"
                title="Close"
              >
                <CloseIcon />
              </button>
            </div>
            <div className="modal-image-wrapper">
              <img
                src={selectedImage?.url}
                alt="Selected"
                className="modal-image"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGallery;
