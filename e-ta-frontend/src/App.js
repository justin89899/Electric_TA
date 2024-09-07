// App.js
import React, { useState, useEffect } from 'react';
import Login from './Login'; // Import your Login component
import './App.css';
import CollapsibleQAItem from './CollapsibleQAItem';
import { ReactComponent as ScholarIcon } from './scholar.svg';
import Logo from './logo.png';


function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [showQaHistory, setShowQaHistory] = useState(false);

  const handleLoginSubmit = async (email, password) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      setIsLoggedIn(true);
      setEmail(email);
      setPassword(password);
    } catch (e) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/logout', {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      setIsLoggedIn(false);
      setEmail('');
      setPassword('');
      setAnswer('');
      setShowQaHistory(false);
    } catch (e) {
      setError('Logout failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load QA history from localStorage when the component mounts
    const savedQaHistory = JSON.parse(localStorage.getItem('qaHistory'));
    if (savedQaHistory) {
      setQaHistory(savedQaHistory);
    }
  }, []);

  const clearHistory = () => {
    setQaHistory([]);
    localStorage.removeItem('qaHistory');
  };

  const deleteHistoryItem = (index) => {
    // Update the qaHistory state to filter out the item at the specific index
    const updatedHistory = qaHistory.filter((_, i) => i !== index);
    setQaHistory(updatedHistory);
    // Update localStorage
    localStorage.setItem('qaHistory', JSON.stringify(updatedHistory));
  };


  const handleSubmitQuestion = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:5000/process-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, email, password }),
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error('Error processing question');
      }

      const { answer, snapshot, url } = data;

      setAnswer(data);
      console.log(answer);
      
      // Update state to include the new Q&A pair
      // setQaHistory(prevHistory => [
      //   ...prevHistory,
      //   { question, answer, snapshot, url }
      // ]);
      setQaHistory(prevHistory => {
        const newHistory = [{ question, answer, snapshot, url }, ...prevHistory];

        // Save to localStorage
        localStorage.setItem('qaHistory', JSON.stringify(newHistory));

        return newHistory;
      });

    } catch (e) {
      setError('Failed to fetch answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        <Login onLogin={handleLoginSubmit} loading={loading} />
      ) : (
        <>
          <div className="header">
            <div className="header-left">
              <img src={Logo} alt="E-TA Logo" className="header-logo" />
              <h4>Your Enhanced Teaching Assistant</h4>
            </div>
            <button onClick={handleLogout} disabled={loading}>
              Logout
            </button>
          </div>
          <div className="question-form">
            <form onSubmit={handleSubmitQuestion}>
              <label htmlFor="question-input"></label>
              <ScholarIcon className="scholar-icon" />
              <input
                id="question-input"
                type="text"
                value={question}
                placeholder="Please ask me questions..."
                onChange={(e) => setQuestion(e.target.value)}
              />
            <button type="submit" disabled={loading || !question} className="icon-button">
              {loading ? (
                'Loading...'
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 50 50">
                  <path d="M 21 3 C 11.622998 3 4 10.623005 4 20 C 4 29.376995 11.622998 37 21 37 C 24.712383 37 28.139151 35.791079 30.9375 33.765625 L 44.085938 46.914062 L 46.914062 44.085938 L 33.886719 31.058594 C 36.443536 28.083 38 24.223631 38 20 C 38 10.623005 30.377002 3 21 3 z M 21 5 C 29.296122 5 36 11.703883 36 20 C 36 28.296117 29.296122 35 21 35 C 12.703878 35 6 28.296117 6 20 C 6 11.703883 12.703878 5 21 5 z"></path>
                </svg>
              )}
            </button>
            </form>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="current-answer-container">
            {answer && !loading && (
              <div className="answer">
                <h2>Explanation:</h2>
                <p>{answer.answer}</p>
                <hr />  {/* Horizontal rule */}
                <h2>Slide Image:</h2>
                {answer.snapshot && (
                  <img src={answer.snapshot} alt="Snapshot related to the answer" />
                )}
                <hr />  {/* Horizontal rule */}
                <h2>Video:</h2>
                {answer.url && (
                  <a href={answer.url} target="_blank" rel="noopener noreferrer">
                    Watch more details about the answer in this video.
                  </a>
                )}
              </div>
            )}
          </div>

          <div className='show-history-and-clear-history-container'>
            {qaHistory.length > 0 && (
              <>
                <button
                  className={`btn btn-link qa-history-toggle ${showQaHistory ? 'active' : ''}`}
                  onClick={() => setShowQaHistory(!showQaHistory)}
                >
                  {showQaHistory ? 'Hide' : 'Show'} Previous Q&A
                </button>
                <button className={'clearHistory'} onClick={clearHistory} disabled={loading}>
                  Clear
                </button>
              </>
            )}
          </div>


          {showQaHistory && qaHistory.map((item, index) => (
            <CollapsibleQAItem
              key={index}
              question={`Q: ${item.question}`}
              answer={item.answer}
              snapshot={item.snapshot}
              url={item.url}
              onDelete={() => deleteHistoryItem(index)}
            />
          ))}
        </>
      )}
    </div>
  );
}

export default App;
