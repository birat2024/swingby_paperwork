// calculate_dailysales.js

// Function to calculate day totals for shift details
function calculateDayTotals() {
    var totalSalesShift1 = parseFloat(document.getElementById('total_sales_shift1').value) || 0;
    var totalSalesShift2 = parseFloat(document.getElementById('total_sales_shift2').value) || 0;
    document.getElementById('total_sales_day').value = (totalSalesShift1 + totalSalesShift2).toFixed(2);

    var cardTotalShift1 = parseFloat(document.getElementById('card_total_shift1').value) || 0;
    var cardTotalShift2 = parseFloat(document.getElementById('card_total_shift2').value) || 0;
    document.getElementById('card_total_day').value = (cardTotalShift1 + cardTotalShift2).toFixed(2);

    var dropTotalShift1 = parseFloat(document.getElementById('drop_total_shift1').value) || 0;
    var dropTotalShift2 = parseFloat(document.getElementById('drop_total_shift2').value) || 0;
    document.getElementById('drop_total_day').value = (dropTotalShift1 + dropTotalShift2).toFixed(2);

    var lottoPayoutShift1 = parseFloat(document.getElementById('lotto_payout_shift1').value) || 0;
    var lottoPayoutShift2 = parseFloat(document.getElementById('lotto_payout_shift2').value) || 0;
    document.getElementById('lotto_payout_day').value = (lottoPayoutShift1 + lottoPayoutShift2).toFixed(2);

    var payout1Shift1 = parseFloat(document.getElementById('payout1_shift1').value) || 0;
    var payout1Shift2 = parseFloat(document.getElementById('payout1_shift2').value) || 0;
    document.getElementById('payout1_day').value = (payout1Shift1 + payout1Shift2).toFixed(2);

    var payout2Shift1 = parseFloat(document.getElementById('payout2_shift1').value) || 0;
    var payout2Shift2 = parseFloat(document.getElementById('payout2_shift2').value) || 0;
    document.getElementById('payout2_day').value = (payout2Shift1 + payout2Shift2).toFixed(2);

    // Calculate over/short
    calculateOverShort();
}

function calculateOverShort() {
    // Assuming over_short is the difference between total sales and sum of other totals
    var totalSalesDay = parseFloat(document.getElementById('total_sales_day').value) || 0;
    var cardTotalDay = parseFloat(document.getElementById('card_total_day').value) || 0;
    var dropTotalDay = parseFloat(document.getElementById('drop_total_day').value) || 0;
    var lottoPayoutDay = parseFloat(document.getElementById('lotto_payout_day').value) || 0;
    var payout1Day = parseFloat(document.getElementById('payout1_day').value) || 0;
    var payout2Day = parseFloat(document.getElementById('payout2_day').value) || 0;

    var overShort = totalSalesDay - (cardTotalDay + dropTotalDay + lottoPayoutDay + payout1Day + payout2Day);
    document.getElementById('over_short').value = overShort.toFixed(2);
}

// Add event listeners to shift detail fields for auto calculation
document.querySelectorAll('.form-control').forEach(item => {
    item.addEventListener('input', calculateDayTotals);
});








