// Wait for the document to fully load before executing JavaScript
document.addEventListener("DOMContentLoaded", function () {
    // Get references to the input fields for each row
    var rows = document.querySelectorAll('tbody tr');

    // Function to calculate row totals
    function calculateRowTotal(row) {
        var shift1Input = row.querySelector('[name$="_shift1"]');
        var shift2Input = row.querySelector('[name$="_shift2"]');
        var dayInput = row.querySelector('[name$="_day"]');

        var shift1Value = parseFloat(shift1Input.value) || 0;
        var shift2Value = parseFloat(shift2Input.value) || 0;

        // Check if the input fields are not greyed out
        if (!shift1Input.disabled && !shift2Input.disabled) {
            var dayTotal = shift1Value + shift2Value;
            dayInput.value = dayTotal.toFixed(2);
        }
    }

    // Function to calculate "Over/Short"
    function calculateOverShort() {
        var totalSalesDay = parseFloat(document.querySelector('[name="total_sales_day"]').value) || 0;
        var cardTotalDay = parseFloat(document.querySelector('[name="card_total_day"]').value) || 0;
        var dropTotalDay = parseFloat(document.querySelector('[name="drop_total_day"]').value) || 0;
        var lottoPayoutDay = parseFloat(document.querySelector('[name="lotto_payout_day"]').value) || 0;
        var payout1Day = parseFloat(document.querySelector('[name="payout1_day"]').value) || 0;
        var payout2Day = parseFloat(document.querySelector('[name="payout2_day"]').value) || 0;
        var dayColumnInput = document.querySelector('[name="over_short"]');

        var overShort = cardTotalDay + dropTotalDay + lottoPayoutDay + payout1Day + payout2Day - totalSalesDay;

        dayColumnInput.value = overShort.toFixed(2);
    }

    // Add event listeners to input fields for live auto calculation
    rows.forEach(function (row) {
        var inputs = row.querySelectorAll('input[type="number"]');
        inputs.forEach(function (input) {
            input.addEventListener('input', function () {
                calculateRowTotal(row);
                calculateOverShort(); // Calculate "Over/Short" whenever any input changes
            });
        });
    });

    // Trigger initial calculation when the page loads
    calculateRowTotal(rows[0]); // Calculate for the first row
    calculateOverShort(); // Calculate "Over/Short" initially
});
