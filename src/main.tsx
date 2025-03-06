import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import App from './App';

const Main = () => (
  <Router>
    <App />
  </Router>
);

ReactDOM.render(<Main />, document.getElementById('root'));
