console.log("calculate_lottery.js is loaded");

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    function calculateRow(row) {
        const amount = parseFloat(row.querySelector('.amount').value) || 0;
        const beginDay = parseFloat(row.querySelector('.begin-day').value) || 0;
        const endDay = parseFloat(row.querySelector('.end-day').value) || 0;

        const sold = endDay - beginDay;
        const total = amount * sold;

        row.querySelector('.sold').textContent = sold;
        row.querySelector('.total').textContent = total.toFixed(2); // Round to 2 decimal places
    }

    function calculateGrandTotal() {
        const totalCells = document.querySelectorAll('.total');
        let grandTotal = 0;
        totalCells.forEach(cell => {
            const value = parseFloat(cell.textContent) || 0;
            grandTotal += value;
        });
        document.querySelector('.grand-total').textContent = grandTotal.toFixed(2);
    }

    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        ['input', 'change'].forEach(eventType => {
            row.querySelectorAll('input').forEach(input => {
                input.addEventListener(eventType, () => {
                    calculateRow(row);
                    calculateGrandTotal(); // Calculate grand total whenever any input changes
                });
            });
        });
        calculateRow(row); // Initial calculation for the row
    });
    calculateGrandTotal(); // Initial calculation for the grand total

    document.getElementById('add-row').addEventListener('click', function() {
        createNewRow();
    });
    
    // Handle click event on 'Remove Row' button
    document.getElementById('remove-row').addEventListener('click', function() {
        removeLastRow();
    });



    // Lotto total section
    function calculateTotal() {
        const totalPos = parseFloat(document.getElementById('total-pos').value) || 0;
        const scratchOff = parseFloat(document.getElementById('scratch-off').value) || 0;
        const lottoOnline = parseFloat(document.getElementById('lotto-online').value) || 0;
        const payoutTotal = parseFloat(document.getElementById('payout-total').value) || 0;

        const total = totalPos - scratchOff - lottoOnline - payoutTotal; // Adjust the formula as needed
        document.getElementById('calculated-total').textContent = total.toFixed(2);
    }

    // Add event listeners
    ['input', 'change'].forEach(eventType => {
        document.getElementById('total-pos').addEventListener(eventType, calculateTotal);
        document.getElementById('scratch-off').addEventListener(eventType, calculateTotal);
        document.getElementById('lotto-online').addEventListener(eventType, calculateTotal);
        document.getElementById('payout-total').addEventListener(eventType, calculateTotal);
    });

    // Initial calculation
    calculateTotal();
});
