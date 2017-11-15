/**
 * Created by pamaron on 08/11/2017.
 */
var x = {
    a: "1",
    b: "2"
};

var text = {
    header: {
        it: {spett: 'Spett.le'},
        en: {spett: 'Dear'}
    },
    body: {
        it: {
            p1: 'Si attesta che ',
            p2: ' ha frequentato la conferenza ',
            p3: ' tenutasi a\nFirenze dal ',
            p4: ' al ',
            p5: '.'
        },
        en: {
            p1: 'This is to certify that ',
            p2: ' attended the conference ',
            p3: ' in \nFlorence from ',
            p4: ' to ',
            p5: '.'
        }
    },
    signature: {
        it: {sign: 'In fede', pres: 'Il presidente'},
        en: {sign: 'Sincerely', pres: 'The president'}
    }
};

function generate_cert(conf_name, date_start, date_end, name, email, lang) {
    var doc = new jsPDF({lineHeight: 1.5});

    //watermark
    var wmark_imgData = images.watermark;
    doc.addImage(wmark_imgData, 'png', 0, 0);
    //APS Logo top left
    var aps_logo_imgData = images.pyton_italia_logo;
    doc.addImage(aps_logo_imgData, 'png', 20, 20);

    // PyCon Logo section top right
    var pycon_logo_imgData = images.pycon_nove_logo;
    doc.addImage(pycon_logo_imgData, 'png', 160, 20);


    // Header
    doc.setFont("helvetica");
    doc.setFontType("bold");
    doc.setFontSize(14);
    doc.text(20, 80, text.header[lang].spett);

    doc.setFontType("normal");
    doc.setFontSize(14);
    doc.text(25, 90, name);
    doc.setFontSize(12);
    doc.setFontType("italic");
    doc.text(25, 95, email);

    doc.setDrawColor(155, 155, 155); // draw gray line
    doc.line(20, 52, 190, 52);

    // Body
    doc.setFontSize(13);
    doc.setFontType("normal");
    doc.text(20, 140, text.body[lang].p1 + name + text.body[lang].p2 + conf_name + text.body[lang].p3 + date_start + text.body[lang].p4 + date_end + text.body[lang].p5);

    // Signature
    doc.setFontSize(14);
    doc.text(152, 180, text.signature[lang].sign);

    doc.setFontType("bold");
    doc.text(140, 190, "Python Italia APS");
    doc.setFontType("italic");
    doc.text(148, 200, text.signature[lang].pres);
    doc.text(137, 207, "Patrick Guido Arminio");
    var president_signature_imgData = images.signature;
    doc.addImage(president_signature_imgData, 'png', 134, 210);

    //footer
    doc.setDrawColor(155, 155, 155); // draw gray line
    doc.line(20, 273, 190, 273);
    doc.setFontSize(9);
    doc.setFontType("normal");
    doc.text(105, 280, 'PYTHON ITALIA Associazione di Promozione Sociale - Via Mugellese, 1 – 50013 - Campi Bisenzio (FI)', null, null, 'center');
    doc.text(105, 284, 'Partita IVA/V.A.T. 05753460483 – Tel/Phone 055.8969650 – email: fatture@pycon.it', null, null, 'center');

    //oc.text(conf_name + date_start + date_end, 12, 50);
    doc.save('Cert_' + conf_name.replace(/ /g, '') + '_' + name.replace(/ /g, '') + '.pdf');
}
