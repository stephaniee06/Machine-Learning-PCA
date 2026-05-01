import { useState } from 'react';
import { uploadCsv } from '../api/client';
import styles from './FileUpload.module.css';

export default function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [labelColumn, setLabelColumn] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    setFile(f || null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a CSV file.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await uploadCsv(file, labelColumn || null);
      if (!result.success) {
        setError(result.error || 'Upload failed');
        return;
      }
      onUploadSuccess(result);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className={styles.section}>
      <h2 className={styles.title}>1. Upload CSV</h2>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.row}>
          <div className={styles.fileCol}>
            <span className={styles.fileLabelText}>CSV file</span>
            <div className={styles.fileInputRow}>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className={styles.input}
                id="csv-file-input"
              />
              {file && <span className={styles.fileName} title={file.name}>{file.name}</span>}
            </div>
          </div>
          <label className={styles.labelField}>
            <span className={styles.labelFieldText}>Label column (optional)</span>
            <input
              type="text"
              placeholder="e.g. label, target, class"
              value={labelColumn}
              onChange={(e) => setLabelColumn(e.target.value)}
              className={styles.labelInput}
            />
          </label>
        </div>
        {error && <p className={styles.error}>{error}</p>}
        <button type="submit" disabled={loading} className={styles.button}>
          {loading ? 'Uploading…' : 'Upload'}
        </button>
      </form>
    </section>
  );
}
