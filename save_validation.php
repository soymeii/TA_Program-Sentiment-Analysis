<?php
require __DIR__ . '/vendor/autoload.php';
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\IOFactory;

if (isset($_POST['validate'])) {

    // ===================== SAVE VALIDATION LABELS =================
    // STEP 1. mengambil data dari form berdasarkan nama variabel
    $accounts = $_POST['account'];
    $reviews  = $_POST['review'];
    $labels   = $_POST['label'];
    $source   = $_POST['source']; // tambahkan hidden input dari form: shopee / tokopedia

    // STEP 2. mengupdate file sumber dengan label yang diberikan
    $sourceFile = "C:/xampp/htdocs/TA/Program/result/preprocessed_from_" . $source . ".xlsx";

    // STEP 3. nge cek terlebih dahulu apakah file sumber (atau hasil preprocessed) ada
    if (!file_exists($sourceFile)) {
        die("File sumber tidak ditemukan: " . $sourceFile);
    }

    // STEP 4.load filesumber
    $spreadsheet = IOFactory::load($sourceFile);
    $sheet = $spreadsheet->getActiveSheet();

    // STEP 4.mengupdate kolom C (index 2) = label berdasarkan input dari form
    $rowIndex = 2;
    foreach ($labels as $i => $lbl) {
        $sheet->setCellValue("C".$rowIndex, $lbl);
        $rowIndex++;
    }

    // STEP 5. save ulang hasil preprocessed 
    $writer = IOFactory::createWriter($spreadsheet, 'Xlsx');
    $writer->save($sourceFile);

    // ===================== DELETE ACCOUNT COLUMN =================
    // STEP 1. load file sumber (hasil preprocessed dengan label)
    $data = $sheet->toArray(null, true, true, true);
    // null  → nilai default untuk cell kosong
    // true  → ambil hasil perhitungan jika cell berisi formula
    // true  → gunakan format tampilan Excel
    // true  → gunakan huruf kolom (A, B, C) sebagai index array

    // STEP 2. hapus kolom account (kolom A)
    foreach ($data as &$row) {
        unset($row['A']);}

    // ===================== CONCAT DATASET (preprocessed file + new_dataset_program) ================= 
    // STEP 1. initialize paths
    $mainDataset = "C:/xampp/htdocs/TA/Program/dataset/new_dataset_program.xlsx";
    #$outputFile  = "C:/xampp/htdocs/TA/Program/dataset/final_training_dataset.xlsx";

    // STEP 2. nge cek apakah dataset utama ada
    if (!file_exists($mainDataset)) {
        die("Dataset utama tidak ditemukan: " . $mainDataset);
    }

    // STEP 3. load dataset utama
    #$main = IOFactory::load($mainDataset)->getActiveSheet()->toArray(null, true, true, true);
    // Load dataset utama
    $main = IOFactory::load($mainDataset);
    $mainSheet = $main->getActiveSheet();
    $mainData = $mainSheet->toArray(null, true, true, true);

    // STEP 4. merge data (tanpa header dari data baru)
    $merged = array_merge($mainData, array_slice($data, 1));

    // STEP 5. Tulis hasil gabungan kembali ke sheet utama
    $mainSheet->fromArray($merged, NULL, "A1");


    // ===================== STEP 4: KONVERSI LABEL KE NUMERIK =================
    $highestRow = $mainSheet->getHighestRow();

    // STEP 6. ubah kolom label yg string ke 0 & 1 -- asumsi kolom label = kolom B 
    for ($row = 2; $row <= $highestRow; $row++) {
        $val = strtolower(trim($mainSheet->getCell("B" . $row)->getValue()));
        if ($val === "positive") {
            $mainSheet->setCellValue("B" . $row, 1);
        } elseif ($val === "negative") {
            $mainSheet->setCellValue("B" . $row, 0);
        }
    }

    // STEP 7. Simpan kembali ke file dataset utama
    $writer = IOFactory::createWriter($main, 'Xlsx');
    $writer->save($mainDataset);

    // ===================== RUN TRAINING SCRIPT =================
    //$command = 'start "" python "C:\\xampp\\htdocs\\TA\\Program\\model\\trainingdata.py"';
    // pclose(popen($command, "r"));
    $command = 'python "C:\\xampp\\htdocs\\TA\\Program\\model\\trainingdata.py"';
    exec($command, $output, $status);   // PHP akan menunggu sampai Python selesai

    // Redirect balik ke index.php dengan pesan notifikasi
    echo "<script>
        alert('Data berhasil divalidasi dan disimpan!');
        window.location.href = 'index.php';
    </script>";
    exit;
    }
?>
