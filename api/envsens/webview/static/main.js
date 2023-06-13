/*all of this expects the following API response format (example):
{
  "data": [
    {
      "time": "2023-05-23 13:08:18", (iso timestamp)
      "co2": 0, (integer)
      "rain": "true", (bool)
      "temp": 0, (integer)
      "press": 0, (integer)
      "humid": 0 (integer)
    },
}
*/
let historic;
let predicted;
let chart;

async function fetch_data() {
    async function json_data(response) {
        json = await response.json();
        return json.data;
    }
    historic = await fetch("/data/historic?days=1&hours=5")
        .then(response => json_data(response));
    predicted = await fetch("/data/predictions?days=3&hours=0")
        .then(response => json_data(response));
}

function array_from_data(data, item) {
    ret = []
    data.forEach(e => {
        if (item === 'time') {
            ret[ret.length] = e[item].split(' ')[1];
        } else {
            ret[ret.length] = e[item];
        }
    })
    return ret
}

const label_lookup = {
    "temp": "Temperatur in °C",
    "co2": "CO2-Menge in",
    "rain": "Regnet es?",
    "press": "Luftdruck in hPa",
    "humid": "Relative Luftfeuchtigkeit in %",
    "particle": "Feinstaubmenge in"
}

function chart_for_data() {
    if (chart !== undefined) chart.destroy();
    const label = document.getElementById('data-select').value;
    chart = new Chart(document.getElementById('datenansicht'), {
        type: 'line',
        data: {
            labels: array_from_data(historic.concat(predicted), 'time'),
            datasets: [
                {
                    label: label_lookup[label],
                    data: array_from_data(historic, label),
                    borderWidth: 2,
                    borderColor: '#b1e053',
                },
                {
                    label: 'Vorhersage',
                    data: array_from_data(predicted, label),
                    borderWidth: 2,
                    borderColor: '#aaaaaa',
                },
            ]
        },
        options: {
            cubicInterpolationMode: 'default',
            scales: {
                y: {
                    beginAtZero: true
                }
            },
        }
    });
}

function init_auto_update() {
    fetch_data()
        .then(() => {
            chart_for_data();
        })
        .then(() => {
            // update chart data every 10 minutes
            setTimeout(init_auto_update, 600000)
        });
}

init_auto_update()
