
// Check if the user's preferred mode is already set (if previously selected)
const userPreferredMode = localStorage.getItem('preferredMode');
if (userPreferredMode) {
  document.body.classList.add(userPreferredMode);
}

// Toggle function
function toggleDarkMode() {
  const body = document.body;

  if (body.classList.contains('dark')) {
    body.classList.remove('dark');
    localStorage.setItem('preferredMode', 'light');
  } else {
    body.classList.add('dark');
    localStorage.setItem('preferredMode', 'dark');
  }
}

// Attach the toggle function to the button
document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);
