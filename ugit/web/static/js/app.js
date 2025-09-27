let currentPath = '';
let currentFiles = [];
let navigationHistory = [];
let latestCommitInfo = null; // Store latest commit info

document.addEventListener('DOMContentLoaded', function() {
    loadLatestCommit();
    loadFiles('');
    
    // Back button functionality
    document.getElementById('back-button').addEventListener('click', goBack);
    document.getElementById('back-to-files').addEventListener('click', showFileList);
    
    // Tab switching
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Refresh commits button
    const refreshBtn = document.getElementById('refresh-commits');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadCommits);
    }
});

async function loadLatestCommit() {
    try {
        // First try the latest-commit endpoint, fallback to files endpoint
        let response = await fetch('/api/latest-commit');
        if (!response.ok && response.status === 404) {
            // Fallback: get commit info from files endpoint
            response = await fetch('/api/files');
        }
        
        const data = await response.json();
        
        if (data.commit) {
            document.getElementById('latest-commit-message').textContent = data.commit.message || 'No commit message';
            document.getElementById('latest-commit-hash').textContent = data.commit.sha ? data.commit.sha.substring(0, 7) : 'N/A';
            document.getElementById('latest-commit-date').textContent = data.commit.timestamp ? formatCommitDate(data.commit.timestamp) : 'N/A';
        }
    } catch (error) {
        console.error('Error loading latest commit:', error);
        document.getElementById('latest-commit-message').textContent = 'Error loading commit';
        document.getElementById('latest-commit-hash').textContent = 'N/A';
        document.getElementById('latest-commit-date').textContent = 'N/A';
    }
}

async function loadFiles(path) {
    try {
        const response = await fetch(`/api/files${path ? '?path=' + encodeURIComponent(path) : ''}`);
        const data = await response.json();
        
        // The API returns {files: [...], commit: {...}, path: "..."} format
        if (data.files) {
            currentPath = path;
            currentFiles = data.files || [];
            latestCommitInfo = data.commit; // Store commit info for file display
            displayFiles(data.files || []);
            updateBreadcrumb(path);
            updateFileCount(data.files ? data.files.length : 0);
            showFileList(); // Make sure file list is visible
        } else {
            console.error('Error: No files in response');
        }
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

function displayFiles(files) {
    const tableBody = document.getElementById('file-table-body');
    tableBody.innerHTML = '';

    files.forEach(file => {
        const row = document.createElement('tr');
        const isDirectory = file.type === 'tree';
        
        // Use file-specific commit info if available
        let commitMessage, commitDate;
        
        if (file.commit_message) {
            // File or directory has commit info from server
            commitMessage = file.commit_message;
            commitDate = formatCommitDate(file.commit_date);
        } else {
            // Fallback for files/directories without commit info
            commitMessage = 'Loading...';
            commitDate = 'Loading...';
        }
        
        row.innerHTML = `
            <td>
                <div class="file-row-name" onclick="handleFileClick('${file.name}', ${isDirectory})">
                    <div class="file-row-icon ${isDirectory ? 'folder' : 'file'}">
                        <i class="fa-solid fa-${isDirectory ? 'folder' : 'file-lines'}"></i>
                    </div>
                    <span class="file-row-text">${file.name}</span>
                </div>
            </td>
            <td>
                <div class="file-commit-message">
                    ${commitMessage}
                </div>
            </td>
            <td>
                <div class="file-commit-date">
                    ${commitDate}
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function updateFileCount(count) {
    document.getElementById('file-count').textContent = `${count} ${count === 1 ? 'item' : 'items'}`;
}

function handleFileClick(fileName, isDirectory) {
    if (isDirectory) {
        // Navigate to directory
        navigationHistory.push(currentPath);
        const newPath = currentPath ? `${currentPath}/${fileName}` : fileName;
        loadFiles(newPath);
        
        // Show back button
        const backButton = document.getElementById('back-button');
        if (backButton) {
            backButton.style.display = 'block';
        }
    } else {
        // View file
        viewFile(fileName);
    }
}

async function viewFile(fileName) {
    const fullPath = currentPath ? `${currentPath}/${fileName}` : fileName;
    
    try {
        const response = await fetch(`/api/file?path=${encodeURIComponent(fullPath)}`);
        const data = await response.json();
        
        // API returns: {path: "...", type: "text/binary", size: 123, content: "...", commit_sha: "..."}
        if (data.path) {
            showFileViewer(fileName, data.content, data.size, data.type);
        } else {
            console.error('Error loading file:', data);
            alert('Error loading file');
        }
    } catch (error) {
        console.error('Error loading file:', error);
        alert('Error loading file');
    }
}

function showFileViewer(fileName, content, size, fileType) {
    // Hide file browser and show file viewer
    document.querySelector('.file-browser').style.display = 'none';
    const fileViewer = document.getElementById('file-viewer');
    fileViewer.style.display = 'block';
    
    // Update file path
    document.getElementById('file-path').textContent = fileName;
    
    // Update file stats
    const sizeKB = (size / 1024).toFixed(1);
    const lines = content ? content.split('\n').length : 0;
    document.getElementById('file-stats').innerHTML = `
        <span>${sizeKB} KB</span>
        <span>•</span>
        <span>${lines} lines</span>
    `;
    
    // Display content
    const contentDiv = document.getElementById('file-content');
    
    if (fileType === 'binary' || isBinaryFile(fileName)) {
        contentDiv.innerHTML = `<div style="padding: 24px; text-align: center; color: #7d8590;">
            <i class="fa-solid fa-file-binary" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
            <p>Binary file (${(size / 1024).toFixed(1)} KB)</p>
            <p>Cannot display binary content</p>
        </div>`;
    } else if (isImageFile(fileName)) {
        contentDiv.innerHTML = `<img src="data:image/${getImageType(fileName)};base64,${btoa(content)}" style="max-width: 100%; height: auto; margin: 24px;">`;
    } else if (content) {
        // Text file - create repository-style code viewer with line numbers
        const lines = content.split('\n');
        const lineNumbers = lines.map((_, index) => index + 1).join('\n');
        
        contentDiv.innerHTML = `
            <div class="line-numbers-wrapper">
                <div class="line-numbers">${lineNumbers}</div>
                <div class="code-content">${escapeHtml(content)}</div>
            </div>
        `;
        
        // Apply syntax highlighting if Prism is available
        if (window.Prism) {
            const codeElement = contentDiv.querySelector('.code-content');
            const language = getLanguageFromFileName(fileName);
            if (language && Prism.languages[language]) {
                codeElement.innerHTML = Prism.highlight(content, Prism.languages[language], language);
                codeElement.classList.add(`language-${language}`);
            }
        }
    } else {
        contentDiv.innerHTML = `<div style="padding: 24px; text-align: center; color: #7d8590;">
            <p>No content to display</p>
        </div>`;
    }
}

function showFileList() {
    // Show file browser and hide file viewer
    document.querySelector('.file-browser').style.display = 'block';
    document.getElementById('file-viewer').style.display = 'none';
}

function goBack() {
    if (navigationHistory.length > 0) {
        const previousPath = navigationHistory.pop();
        loadFiles(previousPath);
        
        // Hide back button if we're at root
        if (navigationHistory.length === 0) {
            const backButton = document.getElementById('back-button');
            if (backButton) {
                backButton.style.display = 'none';
            }
        }
    }
}

function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    const pathParts = path ? path.split('/') : [];
    
    // Root item
    let breadcrumbHTML = `
        <span class="breadcrumb-item root">
            <i class="fa-solid fa-house"></i>
            <span class="breadcrumb-text" onclick="loadFiles('')">ugit</span>
        </span>
    `;
    
    // Add path parts
    let currentPath = '';
    pathParts.forEach((part, index) => {
        currentPath += (currentPath ? '/' : '') + part;
        const isLast = index === pathParts.length - 1;
        
        breadcrumbHTML += `
            <span class="breadcrumb-item ${isLast ? 'active' : ''}">
                <span class="breadcrumb-text" onclick="loadFiles('${currentPath}')">${part}</span>
            </span>
        `;
    });
    
    breadcrumb.innerHTML = breadcrumbHTML;
}

// Utility functions
function isImageFile(fileName) {
    const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'];
    return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
}

function getImageType(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    return ext === 'jpg' ? 'jpeg' : ext;
}

function isBinaryFile(fileName) {
    const binaryExtensions = ['.exe', '.bin', '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z', '.deb', '.rpm'];
    return binaryExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
}

function getLanguageFromFileName(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    const languageMap = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'bash',
        'fish': 'bash',
        'ps1': 'powershell',
        'html': 'markup',
        'xml': 'markup',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'toml': 'toml',
        'ini': 'ini',
        'cfg': 'ini',
        'conf': 'nginx',
        'sql': 'sql',
        'md': 'markdown',
        'tex': 'latex',
        'r': 'r',
        'matlab': 'matlab',
        'm': 'matlab'
    };
    return languageMap[ext] || 'text';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Tab switching functionality
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load content based on tab
    if (tabName === 'commits') {
        loadCommits();
    }
}

// Load commits from API
async function loadCommits() {
    try {
        const response = await fetch('/api/commits');
        const data = await response.json();
        
        if (data.commits) {
            displayCommits(data.commits);
        } else {
            console.error('No commits in response');
            displayCommitsError('No commits found');
        }
    } catch (error) {
        console.error('Error loading commits:', error);
        displayCommitsError('Error loading commits');
    }
}

// Display commits in the commits list
function displayCommits(commits) {
    const commitsList = document.getElementById('commits-list');
    commitsList.innerHTML = '';
    
    if (!commits || commits.length === 0) {
        commitsList.innerHTML = '<div class="empty-commits">No commits found in this repository</div>';
        return;
    }
    
    commits.forEach(commit => {
        const commitItem = document.createElement('div');
        commitItem.className = 'commit-item';
        
        const shortSha = commit.sha ? commit.sha.substring(0, 7) : 'N/A';
        const message = commit.message || 'No commit message';
        const author = commit.author || 'Unknown';
        const date = commit.timestamp ? formatDate(commit.timestamp) : 'Unknown date';
        
        commitItem.innerHTML = `
            <div class="commit-avatar">
                <i class="fa-solid fa-user"></i>
            </div>
            <div class="commit-info">
                <div class="commit-title">${escapeHtml(message)}</div>
                <div class="commit-meta">
                    <span class="commit-author">${escapeHtml(author)}</span>
                    <span class="commit-date">${date}</span>
                    <span class="commit-sha">${shortSha}</span>
                </div>
            </div>
        `;
        
        commitsList.appendChild(commitItem);
    });
}

// Display commits error
function displayCommitsError(message) {
    const commitsList = document.getElementById('commits-list');
    commitsList.innerHTML = `
        <div class="commits-error">
            <i class="fa-solid fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

// Format timestamp to readable date
function formatDate(timestamp) {
    try {
        let date;
        // Handle both Unix timestamps (numbers) and ISO strings
        if (typeof timestamp === 'string') {
            date = new Date(timestamp);
        } else if (typeof timestamp === 'number') {
            date = new Date(timestamp * 1000); // Convert Unix timestamp to milliseconds
        } else {
            return 'Invalid date';
        }
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return 'Invalid date';
        }
        
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Invalid date';
    }
}

// Format file size in bytes to human readable
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

// Format commit date for file table (more compact than commit list)
function formatCommitDate(timestamp) {
    try {
        // Handle invalid timestamps
        if (!timestamp) {
            return 'unknown';
        }
        
        let date;
        // Handle both Unix timestamps (numbers) and ISO strings
        if (typeof timestamp === 'string') {
            date = new Date(timestamp);
        } else if (typeof timestamp === 'number') {
            date = new Date(timestamp * 1000);
        } else {
            return 'unknown';
        }
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return 'unknown';
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays === 0) {
            if (diffMinutes < 1) {
                return 'now';
            } else if (diffMinutes < 60) {
                return diffMinutes === 1 ? '1 minute ago' : diffMinutes + ' minutes ago';
            } else {
                return diffHours === 1 ? '1 hour ago' : diffHours + ' hours ago';
            }
        } else if (diffDays === 1) {
            return 'yesterday';
        } else if (diffDays < 7) {
            return diffDays + ' days ago';
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return weeks === 1 ? '1 week ago' : weeks + ' weeks ago';
        } else if (diffDays < 365) {
            const months = Math.floor(diffDays / 30);
            return months === 1 ? '1 month ago' : months + ' months ago';
        } else {
            const years = Math.floor(diffDays / 365);
            return years === 1 ? '1 year ago' : years + ' years ago';
        }
    } catch (error) {
        return 'unknown';
    }
}