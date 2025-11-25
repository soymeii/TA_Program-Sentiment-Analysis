<!-- composer require phpoffice/phpspreadsheet -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Program.com</title>
    <link rel="stylesheet" type="text/css" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>
<body>
    <h1 class="title">Selamat datang di SentimenSense</h1>
    <p class="subtitle">Masukkan URL produk dari Shopee atau Tokopedia untuk menganalisis sentimen review pelanggan.</p>
    <form action="index.php" method="POST">
        <p>URL PRODUK (shopee / tokopedia) : <input type="text" name="url" placeholder="Masukkan URL Produk" required><br>
        <!-- input reviw count -->
        <p>Jumlah review yang ingin di crawling : <input type="number" name="review_count" placeholder="Masukkan Jumlah Review" min="1" required><br>
        <button class="button button1" type="submit" name="search">Analisis</button>
    </form>

    <!-- ----------------------------------------------------------------------------------------------------------------------------------- -->
    <?php
    set_time_limit(0);

    use PhpOffice\PhpSpreadsheet\IOFactory;

    if (isset($_POST['search'])) {
        // ambil dari inputan form untuk POST
        $url = $_POST['url'];
        $review_count = intval($_POST['review_count']);

        // echo "<p>Jumlah Review: " . htmlspecialchars($review_count) . "<p>";
        // echo "<p>Product URL :" . htmlspecialchars($url) . "<p>";

        // pilih script berdasarkan domain
        if (strpos($url, "shopee.co.id") !== false || strpos($url, "id.shp.ee") !== false) {
            $source = "shopee";
            // $command = escapeshellcmd("python shopee.py \"$url\" $review_count");
            $command = 'start "" python "C:\\xampp\\htdocs\\TA\\Program\\shopee.py" "'.$url.'" '.$review_count;
            $info_path = "C:/xampp/htdocs/TA/Program/result/information_from_shopee.xlsx";
            $excel_path = "C:/xampp/htdocs/TA/Program/result/crawling_from_shopee.xlsx";
            $prediction_path = "C:/xampp/htdocs/TA/Program/result/preprocessed_from_shopee.xlsx";
        } elseif (strpos($url, "tokopedia.com") !== false) {
            $source = "tokopedia";
            // $command = escapeshellcmd("python tokopedia.py \"$url\" $review_count");
            $command = 'start "" python "C:\\xampp\\htdocs\\TA\\Program\\tokopedia.py" "'.$url.'" '.$review_count;
            $info_path = "C:/xampp/htdocs/TA/Program/result/information_from_tokopedia.xlsx"; // buat ngambil info produk
            $excel_path = "C:/xampp/htdocs/TA/Program/result/crawling_from_tokopedia.xlsx"; // buat ngambil account & review
            $prediction_path = "C:/xampp/htdocs/TA/Program/result/preprocessed_from_tokopedia.xlsx"; //buat ngambil label
        } else {
            die("Domain tidak dikenali. Hanya Shopee & Tokopedia.");
        }

        // jalankan Python script
        $output = shell_exec($command);
        echo "<pre>$output</pre>";

        // ===================== SHOW INFORMATION PRODUCT =================

        if (file_exists($info_path)) {
            require __DIR__ . '/vendor/autoload.php'; // penting!!!

            $spreadsheet = IOFactory::load($info_path);
            $sheet = $spreadsheet->getActiveSheet();
            $rows = $sheet->toArray();
            $image_url = $rows[1][0];
            echo '<img src="' . htmlspecialchars($image_url) . '" alt="Product Image" width="200"><br>';
            // echo "<p> image URL: " . htmlspecialchars($rows[1][0]) . "</p>";

            echo "<form id='product-info-form'>";
            echo "<h2>Hasil Crawling Information</h2>";
            echo "<p><b>Product URL: </b>" . htmlspecialchars($url) . "<p>";
            echo "<p><b>Nama Produk: </b>" . htmlspecialchars($rows[1][1]) . "</p>"; //[baris][kolom]
            echo "<p><b> Harga Produk: </b>" . htmlspecialchars($rows[1][2]) . "</p>";
            echo "<p><b> Deskripsi Produk: </b><br>" . nl2br(htmlspecialchars($rows[1][3])) . "</p>"; //nl2br = mengubah \n menjadi <br>
            echo "<p><b> Lokasi Penjual: </b>" . htmlspecialchars($rows[1][4]) . "</p>";
            echo "</form>";
            echo "<br>";

        }


        // ===================== SHOW CRAWLING RESULT & VALIDATION FORM =================
        if (file_exists($excel_path)) {

            require __DIR__ . '/vendor/autoload.php';

            // Load file crawling
            $spreadsheet = IOFactory::load($excel_path);
            $sheet = $spreadsheet->getActiveSheet();
            $rows = $sheet->toArray();

            // Load file prediksi (jika ada)
            // $prediction_path = "C:/xampp/htdocs/TA/Program/result/preprocessed_from_tokopedia.xlsx";
            $prediction_rows = [];
            $label_col_index = null;

            if (file_exists($prediction_path)) {
                $prediction_sheet = IOFactory::load($prediction_path)->getActiveSheet();
                $prediction_rows = $prediction_sheet->toArray();
                // cari index kolom "label"
                $label_col_index = array_search("label", array_map('strtolower', $prediction_rows[0]));
            }
            echo "<br>";
            echo '<form action="save_validation.php" method="POST">'; // NEW FORM
            echo '<h2>Hasil Crawling Review + Sentimen</h2>';
            echo '<div class="card">';
            echo '<div class="scroll-table">';
            echo "<table>";
            echo "<tr><th>No</th><th>Account</th><th>Review</th><th>Label</th></tr>";

            $no = 1; //counter urutan nomor

            // loop mulai baris ke 1 (baris 0 = header)
            for ($i = 1; $i < count($rows); $i++) {

                //[baris][kolom]
                $account = $rows[$i][0]; // ambil kolom pertama = account
                $review  = $rows[$i][1]; // ambil kolom kedua = review

                // Ambil label hasil prediksi, kalau ada. Jika tidak, pakai "-"
                $label = ($label_col_index !== null && isset($prediction_rows[$i][$label_col_index]))
                        ? $prediction_rows[$i][$label_col_index]
                        : "-";

                echo "<tr>";
                echo "<td>$no</td>";
                echo "<td>" . htmlspecialchars($account) . "</td>";
                echo "<td>" . htmlspecialchars($review) . "</td>";

                //htmlspecialchars digunakan untuk mengonversi karakter khusus HTML (seperti < dan >) menjadi entitas HTML (&lt; dan &gt;) 

                // Ubah LABEL jadi dropdown
                echo "<td>
                        <select name='label[$i]'>
                            <option value='positive' ".($label=='positive'?'selected':'').">positive</option>
                            <option value='negative' ".($label=='negative'?'selected':'').">negative</option>
                        </select>
                    </td>";

                // Kirim ulang data account & review biar bisa disimpan lagi
                echo "<input type='hidden' name='account[$i]' value='".htmlspecialchars($account)."'>";
                echo "<input type='hidden' name='review[$i]' value='".htmlspecialchars($review)."'>";

                echo "</tr>";
                $no++;
            }

            echo "</table>";
            echo "</div>";
            echo "</div>";

            echo "<input type='hidden' name='source' value='".htmlspecialchars($source)."'>";

            // ✅ Tombol Simpan
            echo '<button type="submit" name="validate">VALIDASI ULANG & SIMPAN </button>';
            echo '</form>';

            // ===================== SHOW SENTIMENT DISTRIBUTION CHART =================
            if (!empty($prediction_rows) && $label_col_index !== null) {
                // Ambil semua label dari hasil prediksi
                //$labels_only = ["positive", "negative", "positive", "negative"]
                $labels_only = array_column(array_slice($prediction_rows, 1), $label_col_index);

                // Hitung jumlah positif dan negatif
                //fn($x) => strtolower($x) === 'positive' --> Untuk setiap nilai $x dalam array, ubah menjadi huruf kecil, dan cek apakah sama dengan 'positive'.
                $positive_count = count(array_filter($labels_only, fn($x) => strtolower($x) === 'positive'));
                $negative_count = count(array_filter($labels_only, fn($x) => strtolower($x) === 'negative'));
                $total_review = $positive_count + $negative_count;

                // echo "<h2>Distribusi Sentimen</h2>";
                
                // echo "<canvas id='sentimentChart'></canvas>";
                echo "
                <div class='chart-container'>
                    <div class='chart-box'>
                        <canvas id='sentimentChart'></canvas>
                    </div>
                </div>";


                // Chart.js script
                echo "
                <script>
                const ctx = document.getElementById('sentimentChart').getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: ['Positive', 'Negative'],
                        datasets: [{
                            label: 'Distribusi Sentimen',
                            data: [$positive_count, $negative_count],
                            backgroundColor: [
                                'rgba(54, 162, 235, 0.7)',
                                'rgba(255, 99, 132, 0.7)'
                            ],
                            borderColor: [
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 99, 132, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    color: '#333',
                                    font: { size: 14 }
                                }
                            },
                            title: {
                                display: true,
                                text: 'Distribusi Sentimen Review',
                                color: '#333',
                                font: { size: 18, weight: 'bold' }
                            }
                        }
                    }
                });
                </script>
                ";

                // Tambahkan display sebelum chart
                echo "<h2>Ringkasan Hasil Sentimen</h2>";
                echo "<p><b>TOTAL REVIEW:</b> $total_review</p>";
                echo "<p><b>TOTAL REVIEW POSITIF:</b> $positive_count</p>";
                echo "<p><b>TOTAL REVIEW NEGATIF:</b> $negative_count</p>";
            }

            

        }

        else {
            echo "<p>File hasil crawling tidak ditemukan.</p>";
        }
        
    }
        
    ?>
</body>
</html>
