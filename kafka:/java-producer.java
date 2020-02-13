import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class Prod {
    public static void csvread(Producer producer) throws IOException {
        long startTime = System.nanoTime();
        String kafkaTopic = "test";
        String row = "";
//        int count=0;
        BufferedReader csvReader = new BufferedReader(new FileReader("/Users/da/Desktop/full.csv"));
        int rowNum = 0;
        while ((row = csvReader.readLine()) != null) {
            String[] values = row.split(",");
            String a = values[0];
            String b = values[1];
            int c = Integer.parseInt(values[2]);
            double d = Double.parseDouble(values[3]);
            JsonObject rowJson = new JsonObject();
            JsonArray jsonArray = new JsonArray();
            for (String value : values) {
                jsonArray.add(new JsonPrimitive(value));
            }
            rowJson.add(Integer.toString(rowNum), jsonArray);
            int finalRowNum = rowNum;
            producer.send(new ProducerRecord<String, String>("test", Integer.toString(rowNum++), rowJson.toString()),
                    new Callback() {
                        @Override
                        public void onCompletion(RecordMetadata recordMetadata, Exception e) {
                            // executes every time a record is successfully sent or an exception is thrown
                            if (e == null) {
                                // successfully sent
                                System.out.println(finalRowNum);
                            } else {
                                System.out.print(finalRowNum);
                                System.out.println(" failed");
                            }
                        }
                    });
//            if (count == 100000) {
//                long endTime = System.nanoTime() - startTime;
//                System.out.print(endTime);
//                break;
//            }
//            count++;
        }
    }
    public static void main(String[] args) throws IOException {
        String bootstrapServers = "localhost:9092";
        String batchSize = "10000";
        String linger = "0"; // the amount of milliseconds for kafka to wait before batching.
        String acks = "0"; // this may result in some data loss, but delivers the lowest latency
        Properties prop = new Properties();
        prop.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        prop.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        prop.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        prop.setProperty(ProducerConfig.BATCH_SIZE_CONFIG, batchSize); // default batch size is 16384 bytes
        prop.setProperty(ProducerConfig.LINGER_MS_CONFIG, linger); // default linger is 0 ms
        prop.setProperty(ProducerConfig.ACKS_CONFIG, acks);
        Producer<String, String> producer = new KafkaProducer<String, String>(prop);
        csvread(producer);
    }
}
