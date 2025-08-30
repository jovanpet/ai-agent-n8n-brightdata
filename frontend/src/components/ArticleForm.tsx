import React, { useState } from 'react';
import { processArticle } from '../services/api';
import './ArticleForm.css';

interface FormData {
    companyDomain: string;
    articleTitle: string;
    article: string;
}

const ArticleForm: React.FC = () => {
    const [formData, setFormData] = useState<FormData>({
        companyDomain: 'www.meta.com',
        articleTitle: 'Meta Unveils “Precision Engagement” — An AI System to Supercharge Political and Commercial Advertising',
        article: 'In a bold move sure to stir debate, Meta announced today the launch of "Precision Engagement," a new AI-driven advertising platform designed to give marketers "unprecedented control" over how ads are targeted across Facebook and Instagram.\n\nAccording to Meta executives, Precision Engagement uses advanced machine learning to analyze user behavior, purchase history, and even "emotional sentiment" expressed in posts and comments. Advertisers will be able to tailor campaigns not just by age and location, but by factors such as political leanings, lifestyle habits, and even moment-to-moment mood.\n\nMeta insists the system is privacy-compliant, stating that all personal data is "aggregated and anonymized." However, critics are already warning that the technology could reignite concerns around surveillance marketing, election manipulation, and mental health exploitation.\n\nThe company has also positioned the platform as a way for smaller organizations to compete with major brands, offering "AI-assisted creative generation" and "automated message optimization" that can adapt ad copy in real time to maximize engagement.\n\nA Meta spokesperson said the platform is built with "responsible AI" principles, but declined to provide details about how sensitive categories (such as race, religion, or sexuality) would be handled.\n\nIndustry analysts suggest the announcement is likely to face immediate regulatory scrutiny, particularly in the US, where lawmakers are already investigating the role of targeted advertising in spreading misinformation.\n\nThe rollout of Precision Engagement will begin with select advertisers this fall, with broader availability expected in early 2026.'
    });
    const [file, setFile] = useState<File | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string>('');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);

            const reader = new FileReader();
            reader.onload = (event) => {
                const content = event.target?.result as string;
                setFormData(prev => ({
                    ...prev,
                    article: content
                }));
            };
            reader.readAsText(selectedFile);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');
        setResult(null);

        // Add a slight delay for better UX
        await new Promise(resolve => setTimeout(resolve, 500));

        try {
            const response = await processArticle(formData);
            setResult(response.data);

            // Scroll to results smoothly
            setTimeout(() => {
                const resultsSection = document.querySelector('.result-section');
                if (resultsSection) {
                    resultsSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }, 100);
        } catch (error: any) {
            setError(error.response?.data?.error || 'Failed to process article');
        } finally {
            setIsSubmitting(false);
        }
    };

    const isFormValid = formData.companyDomain && formData.articleTitle && formData.article;

    return (
        <div className="article-form-container">
            <form onSubmit={handleSubmit} className="article-form">
                <div className="form-group">
                    <label htmlFor="companyDomain">Company Domain</label>
                    <input
                        type="text"
                        id="companyDomain"
                        name="companyDomain"
                        value={formData.companyDomain}
                        onChange={handleInputChange}
                        placeholder="e.g. techcorp.com"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="articleTitle">Article Title</label>
                    <input
                        type="text"
                        id="articleTitle"
                        name="articleTitle"
                        value={formData.articleTitle}
                        onChange={handleInputChange}
                        placeholder="e.g. The Future of AI Technology"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="article">Article Content</label>
                    <div className="article-input-section">
                        <textarea
                            id="article"
                            name="article"
                            value={formData.article}
                            onChange={handleInputChange}
                            placeholder="Write or paste your article content here... Minimum 50 characters required for processing."
                            rows={10}
                            required
                        />
                        <div className="file-upload-section">
                            <label htmlFor="file" className="file-upload-label">
                                Or upload a document instead:
                            </label>
                            <input
                                type="file"
                                id="file"
                                accept=".txt,.md,.doc,.docx"
                                onChange={handleFileChange}
                            />
                            {file && <span className="file-name">Selected: {file.name}</span>}
                        </div>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={!isFormValid || isSubmitting}
                    className={`submit-button ${isSubmitting ? 'loading' : ''}`}
                >
                    {isSubmitting ? 'Processing...' : 'Process Article for n8n'}
                </button>
            </form>

            {error && (
                <div className="error-message">
                    <h3>Error:</h3>
                    <p>{error}</p>
                </div>
            )}

            {result && (
                <div className="result-section">
                    <h3>{result.success ? 'Successfully Sent to n8n!' : 'Processing Complete'}</h3>
                    {result.success && (
                        <div className="success-message">
                            <p>{result.message}</p>
                            {result.n8n_response && (
                                <div>
                                    <h4>n8n Response:</h4>
                                    <pre className="json-output">{JSON.stringify(result.n8n_response, null, 2)}</pre>
                                </div>
                            )}
                        </div>
                    )}
                    {!result.success && (
                        <div className="warning-message">
                            <p>{result.message}</p>
                        </div>
                    )}
                    <div>
                        <h4>Processed Data:</h4>
                        <pre className="json-output">{JSON.stringify(result.processed_data || result, null, 2)}</pre>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ArticleForm;