import React, {useState} from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import ImageGallery from './components/ImageGallery';
import './App.css';
import ImageUploader from './components/ImageUploader';
import Header from "./components/Header";
import ImageGallery2 from "./components/ImageGallery2";

const App = () => {
    const [images, setImages] = useState([]);

    return (
        <Router>
            <div className="App">
                <Header/>
                <Routes>
                    <Route path="/gallery/:UUID" element={<ImageGallery2/>}/>
                    <Route
                        path="/gallery"
                        element={<ImageGallery2 images={images}/>}
                    />
                    <Route path="/upload" element={<ImageUploader/>}/>
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
