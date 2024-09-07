import React, { useState } from 'react';
import ArrowIcon from './Arrow';

const CollapsibleQAItem = ({ question, answer, snapshot, url, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = () => setIsOpen(!isOpen);

  const deleteIcon = (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
      <path d="M 10 2 L 9 3 L 4 3 L 4 5 L 5 5 L 5 20 C 5 20.522222 5.1913289 21.05461 5.5683594 21.431641 C 5.9453899 21.808671 6.4777778 22 7 22 L 17 22 C 17.522222 22 18.05461 21.808671 18.431641 21.431641 C 18.808671 21.05461 19 20.522222 19 20 L 19 5 L 20 5 L 20 3 L 15 3 L 14 2 L 10 2 z M 7 5 L 17 5 L 17 20 L 7 20 L 7 5 z M 9 7 L 9 18 L 11 18 L 11 7 L 9 7 z M 13 7 L 13 18 L 15 18 L 15 7 L 13 7 z"></path>
    </svg>
  );

  return (
    <div className={`collapsible-qa-item ${isOpen ? 'open' : ''}`}>
      <div className="question-and-delete-container">
        <button onClick={toggleOpen} className="question-toggle">
          <ArrowIcon className={`arrow ${isOpen ? 'open' : ''}`} />
          {question}
        </button>
        <button className="delete-btn" onClick={onDelete}>{deleteIcon}</button>
      </div>
      {isOpen && (
        <div className="answer">
          <h2>Explanation:</h2>
          <p>{answer}</p>
          <hr />  {/* Horizontal rule */}
          <h2>Slide Image:</h2>
          {snapshot && (
            <img src={snapshot} alt="Snapshot related to the answer" />
          )}
          <hr />  {/* Horizontal rule */}
          <h2>Video:</h2>
          {url && (
            <a href={url} target="_blank" rel="noopener noreferrer">
              Watch more details about the answer in this video.
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default CollapsibleQAItem;
