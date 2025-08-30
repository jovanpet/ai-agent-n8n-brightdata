import React from 'react';
import './App.css';
import ArticleForm from './components/ArticleForm';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Article Processing for n8n</h1>
                <p>Submit articles to be processed and sent to n8n workflow</p>
            </header>
            <main className="App-main">
                <ArticleForm />
            </main>
        </div>
    );
}

export default App;
