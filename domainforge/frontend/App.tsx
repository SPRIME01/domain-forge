import React from "react";
import ChatInterface from "./ChatInterface";
import DomainModelVisualizer from "./DomainModelVisualizer";

const App: React.FC = () => {
  return (
    <div className="app-container">
      <ChatInterface />
      <DomainModelVisualizer />
    </div>
  );
};

export default App;
