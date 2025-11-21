import React, { useState } from 'react';
import './SearchBar.css';

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder='Search: e.g., "Brooklyn 2022 pedestrian crashes"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="search-btn">
          🔍 Search
        </button>
      </form>
      <p className="search-hint">
        Try: "Manhattan 2021 cyclist", "Queens pedestrian killed", "Brooklyn 2020"
      </p>
    </div>
  );
}

export default SearchBar;

