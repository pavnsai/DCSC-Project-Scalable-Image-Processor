import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ImageGallery from './components/ImageGallery';
import './App.css';
import ImageUploader from './components/ImageUploader';
import Header from "./components/Header";

const App = () => {
  const [images, setImages] = useState([]);

  return (
    <Router>
      <div className="App">
         <Header />
        <h1>Image Gallery</h1>
        <Routes>
          <Route
            path="/gallery"
            element={<ImageGallery images={images} />}
          />
          <Route path="/upload" element={<ImageUploader />} />
          <Route
            path="/"
            element={
              <div>
                <p>Welcome to the Image Processing App. Navigate to /gallery or /upload.</p>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
