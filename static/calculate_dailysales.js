document.addEventListener("DOMContentLoaded", function () {
    // Function to calculate row totals
    function calculateRowTotal(shift1Name, shift2Name, dayName) {
        var shift1Input = document.querySelector(`[name="${shift1Name}"]`);
        var shift2Input = document.querySelector(`[name="${shift2Name}"]`);
        var dayInput = document.querySelector(`[name="${dayName}"]`);

        var shift1Value = parseFloat(shift1Input.value) || 0;
        var shift2Value = parseFloat(shift2Input.value) || 0;

        var dayTotal = shift1Value + shift2Value;
        dayInput.value = dayTotal.toFixed(2);
    }

    // Function to calculate "Over/Short"
    function calculateOverShort() {
        var totalSalesDay = parseFloat(document.querySelector('[name="total_sales_day"]').value) || 0;
        var cardTotalDay = parseFloat(document.querySelector('[name="card_total_day"]').value) || 0;
        var dropTotalDay = parseFloat(document.querySelector('[name="drop_total_day"]').value) || 0;
        var lottoPayoutDay = parseFloat(document.querySelector('[name="lotto_payout_day"]').value) || 0;
        var payout1Day = parseFloat(document.querySelector('[name="payout1_day"]').value) || 0;
        var payout2Day = parseFloat(document.querySelector('[name="payout2_day"]').value) || 0;
        var overShortInput = document.querySelector('[name="over_short"]');

        var overShort = (cardTotalDay + dropTotalDay + lottoPayoutDay + payout1Day + payout2Day) - totalSalesDay;
        overShortInput.value = overShort.toFixed(2);
    }

    // Add event listeners to input fields for live auto calculation
    var inputNames = ["total_sales_shift1", "total_sales_shift2", "card_total_shift1", "card_total_shift2", "drop_total_shift1", "drop_total_shift2", "lotto_payout_shift1", "lotto_payout_shift2", "payout1_shift1", "payout1_shift2", "payout2_shift1", "payout2_shift2"];
    inputNames.forEach(function(name) {
        var input = document.querySelector(`[name="${name}"]`);
        input.addEventListener('input', function () {
            calculateRowTotal("total_sales_shift1", "total_sales_shift2", "total_sales_day");
            calculateRowTotal("card_total_shift1", "card_total_shift2", "card_total_day");
            calculateRowTotal("drop_total_shift1", "drop_total_shift2", "drop_total_day");
            calculateRowTotal("lotto_payout_shift1", "lotto_payout_shift2", "lotto_payout_day");
            calculateRowTotal("payout1_shift1", "payout1_shift2", "payout1_day");
            calculateRowTotal("payout2_shift1", "payout2_shift2", "payout2_day");
            calculateOverShort();
        });
    });

    // Trigger initial calculation when the page loads
    calculateOverShort(); // Calculate "Over/Short" initially
});
