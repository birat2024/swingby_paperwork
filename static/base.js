document.addEventListener('DOMContentLoaded', function () {
    // Load the selected store from cookies
    var selectedStoreId = getCookie('selectedStoreId');
    var selectedStoreName = getCookie('selectedStoreName');

    // Set the default value in the dropdown
    var dropdown = document.getElementById('storeDropdown');
    if (selectedStoreId) {
        dropdown.value = selectedStoreId;
        document.getElementById('selectedStoreName').innerText = selectedStoreName;
    }

    // Add event listener to update cookies when the selection changes
    dropdown.addEventListener('change', function () {
        var selectedOption = dropdown.options[dropdown.selectedIndex];
        var storeId = selectedOption.value;
        var storeName = selectedOption.text;

        // Update cookies
        setCookie('selectedStoreId', storeId);
        setCookie('selectedStoreName', storeName);

        // Update the displayed store name
        document.getElementById('selectedStoreName').innerText = storeName;
    });
});

// Function to set a cookie
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

// Function to get a cookie value
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}
