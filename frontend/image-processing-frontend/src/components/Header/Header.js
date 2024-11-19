import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
        <div className="logo">
                <Link to="/" className="nav-link">Image Processing App</Link>
        </div>
        <nav>
            <ul className="nav-links">
                <li>
                    <Link to="/processed" className="nav-link">Processed Images</Link>
          </li>
          <li>
            <Link to="/upload" className="nav-link">Upload Images</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
