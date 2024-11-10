import React from 'react';
import './ImageGallery.css';

const ImageGallery = ({ images }) => {
  if (!images.length) return <div>No images found.</div>;

  return (
    <div className="gallery">
      {images.map((image, index) => (
        <div key={index} className="image-item">
          <img src={image.url} alt={`Image ${index + 1}`} />
          <p>{image.file_name.split('/').pop()}</p>
        </div>
      ))}
    </div>
  );
};

export default ImageGallery;
