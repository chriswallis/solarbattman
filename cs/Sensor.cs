using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace SolarBattMan
{
    public class Sensor
    {
        [JsonPropertyName("cid")]
        public string Cid { get; set; }

        [JsonPropertyName("sid")]
        public string Sid { get; set; }

        [JsonPropertyName("units")]
        public string Units { get; set; }

        [JsonPropertyName("age")]
        public int Age { get; set; }

        [JsonPropertyName("data")]
        public DataValue[] Data { get; set; }

        public int Value
        {
            get
            {
                if (Data != null)
                {
                    foreach (var v in Data[0].TheData.Values)
                    {
                        return int.Parse(v.ToString());
                    }
                }
                return 0;
            }
        }
    }

    public class DataValue
    {
        [JsonExtensionData]
        public IDictionary<string, object> TheData { get; set; }
    }
}