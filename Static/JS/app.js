function showSignupForm() {
    document.getElementById('signupForm').style.display = 'block';
    document.getElementById('signinForm').style.display = 'none';
}

function showSigninForm() {
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('signinForm').style.display = 'block';
}

function signup() {
    const userData = {
        username: document.getElementById('signupUsername').value,
        email: document.getElementById('signupEmail').value,
        password: document.getElementById('signupPassword').value
    };

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "success") {
            showSigninForm(); // Redirect user to login form upon successful signup
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function signin() {
    const userData = {
        username: document.getElementById('signinUsername').value,
        password: document.getElementById('signinPassword').value
    };

    fetch('/signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.redirect) {
            // Redirect to the provided URL if login was successful and a redirect URL is present
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function uploadFile() {
    const formData = new FormData();
    const fileField = document.querySelector('input[type="file"]');
    
    formData.append('file', fileField.files[0]);
    
    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showToast(result.message, '#28a745'); // Green for success messages
        }
        if (result.error) {
            showToast(result.error, '#dc3545'); // Red for error messages
        }
        console.log('Success:', result);
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred during the file upload.', '#dc3545'); // Red for catch errors
    });
}

function showToast(message, backgroundColor = '#007bff') { // Default blue background
    const toastId = `toast-${Date.now()}`;
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="5000" style="min-width: 200px; background-color: ${backgroundColor};">
            <div class="toast-header" style="color: #fff; background-color: ${backgroundColor};">
                <strong class="mr-auto">Notification</strong>
                <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body" style="color: #fff;">
                ${message}
            </div>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer');
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = new bootstrap.Toast(document.getElementById(toastId)); // Initialize the toast
    toastElement.show(); // Show the toast
}

function logout() {
    fetch('/logout', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Redirect to login page
        window.location.href = '/'; // Assuming your sign-in page URL is '/'
    })
    .catch(error => {
        console.error('Logout Error:', error);
    });
}

function fetchFiles() {
    fetch('/files', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(files => {
        const fileListElement = document.getElementById('fileList');
        if (fileListElement) {
            fileListElement.innerHTML = ''; // Clear existing list
            files.forEach(file => {
                let fileItem = document.createElement('li');
                fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                fileItem.innerHTML = `
                    ${file.filename} 
                    <span class="badge badge-primary badge-pill">${(file.filesize / 1024).toFixed(2)} KB</span>
                    <button onclick="deleteFile(${file.id})" class="btn btn-danger btn-sm">Delete</button>
                `;
                fileListElement.appendChild(fileItem);
            });
        } else {
            console.error("Element with ID 'fileList' not found.");
        }
    })
    .catch(error => {
        console.error('Error fetching files:', error);
    });
}


function deleteFile(fileId) {
    fetch(`/files/${fileId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(result => {
        showToast(result.message, '#dc3545'); // Show notification
        fetchFiles(); // Refresh the list after deletion
    })
    .catch(error => {
        console.error('Error deleting file:', error);
        showToast('Error deleting file.', '#dc3545');
    });
}

// Admin functions
function listUsers() {
    fetch('/admin/users', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(users => {
        const userListElement = document.getElementById('userList');
        userListElement.innerHTML = ''; // Clear existing list
        users.forEach(user => {
            let userItem = document.createElement('li');
            userItem.className = 'list-group-item';
            userItem.innerHTML = `
                ${user.username} - ${user.email}
                <button onclick="deleteUser(${user.id})" class="btn btn-danger btn-sm float-right">Delete</button>
            `;
            userListElement.appendChild(userItem);
        });
    })
    .catch(error => {
        console.error('Error fetching users:', error);
    });
}

function deleteUser(userId) {
    fetch(`/admin/user/${userId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(result => {
        showToast(result.message, '#dc3545'); // Show notification for success or error
        listUsers(); // Refresh the list after deletion
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        showToast('Error deleting user.', '#dc3545');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Your existing file fetching for general users
    fetchFiles(); 

    // Check if the current page is the admin dashboard
    // This assumes your admin dashboard's URL ends with 'admin.html'
    // You might need to adjust the condition based on your actual URL structure
    if (window.location.href.indexOf('admin.html') > -1) {
        listUsers(); // Automatically list users if on the admin page
    }

    // Existing code for attaching event to 'listUsersButton', if present
    if (document.getElementById('listUsersButton')) {
        document.getElementById('listUsersButton').addEventListener('click', listUsers);
    }

    // You can add more admin-specific event listeners or initialization code here
});

