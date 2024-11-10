import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="logo">
        <h1>Image Processing App</h1>
      </div>
      <nav>
        <ul className="nav-links">
          <li>
            <Link to="/gallery" className="nav-link">Image Gallery</Link>
          </li>
          <li>
            <Link to="/upload" className="nav-link">Image Uploader</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
