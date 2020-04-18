using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace SolarBattMan
{ 
    class Program
    {
        const string SolarSensorSid = "793983";
        const string UsageSensorSid = "833355";

        private static readonly HttpClient client = new HttpClient();

        static async Task Main(string[] args)
        {
            while (true)
            { 
                var sensors = await ProcessRepositories();

                var solarSensor = sensors.Where(s => s.Sid == SolarSensorSid).FirstOrDefault();
                var usageSensor = sensors.Where(s => s.Sid == UsageSensorSid).FirstOrDefault();

                var solarExcess = solarSensor.Value - usageSensor.Value;
                var sign = solarExcess < 0 ? "" : "+";
                var msg = string.Format("{0}{1}W", sign, solarExcess);

                Console.WriteLine(msg);
                Thread.Sleep(10000);
            }
        }

        private static async Task<List<Sensor>> ProcessRepositories()
        {
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            client.DefaultRequestHeaders.Add("User-Agent", "SolarBattMan");

            var streamTask = client.GetStreamAsync("http://www.energyhive.com/mobile_proxy/getCurrentValuesSummary?token=3TAoBW0SidCO90NH3K8rDKP1FVJmhWQB");
            var sensors = await JsonSerializer.DeserializeAsync<List<Sensor>>(await streamTask);
            return sensors;
        }
    }
}
