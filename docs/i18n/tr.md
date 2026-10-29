# Pixel Art Game Studio

[← Ana README](../../README.md) · Türkçe · Makine destekli çeviri; anadili Türkçe olan biri tarafından incelenmeyi bekliyor.

<!-- section: overview -->
## Genel bakış

Pixel Art Game Studio, özgün 2D piksel sanatı oyunlar geliştirmek için hazırlanmış bir Claude Code
becerisi (skill) ve sekiz uzman alt ajandan (subagent) oluşan bir ekiptir. Siz hayal ettiğiniz oyunu,
mevcut sonuçta beğenmediğiniz şeyleri ve bir sonraki adımda neyin değişmesini istediğinizi
anlatırsınız. Claude işi planlar, kodu yazar, grafikleri üretir, testleri çalıştırır, yeniden
üretebildiği hataları düzeltir ve yalnızca gerçekten doğruladığı şeyleri raporlar.

Sıcak ve huzurlu hikâye maceraları, yaşam ve çiftlik simülasyonları, diyalog ağırlıklı rol yapma
oyunları, yukarıdan bakışlı keşif oyunları ve bulmaca oyunları için tasarlanmıştır; ancak başka özgün
2D fikirler için de kullanılabilir. Dört parça birbirinden ayrı tutulur: **beceri** (talimatlar),
**ajanlar** (uzmanlar), **betikler** (deterministik araçlar) ve **oyununuz** (kendi proje dizini).

<!-- section: features -->
## Özellikler

- Gevşek bir fikri kısa bir tasarıma ve oynanabilir en küçük döngüye dönüştüren bir Game Director
  akışı.
- Sorumlulukları net, araç listeleri sınırlı ve raporları yapılandırılmış sekiz uzman.
- Prosedürel piksel sanatı: JSON tanımları gerçek PNG sprite sayfalarına, meta verilere ve
  önizlemelere dönüşür. Aynı tanım her zaman aynı baytları üretir.
- Haritalar, dekor, diyaloglar, görevler, eşyalar ve çeviriler için bir veri sözleşmesi ve
  ulaşılamayan çıkışları, imkânsız diyalog dallarını ve eksik metin anahtarlarını bulan bir doğrulayıcı.
- Önem dereceleri, yeniden üretilebilir hata raporları ve regresyon testleriyle doğrulanmış
  düzeltmeler içeren kalite güvencesi.
- Deneme çalıştırması, çakışma tespiti, yedekleme ve dikkatli kaldırma özelliği olan güvenli bir
  kurulum aracı.

<!-- section: agents -->
## Ajan ekibi

Dokuz rol vardır. **Game Director** becerinin kendisidir ve ana Claude Code oturumunuzda çalışır:
tasarımı korur, görev tanımlarını yazar, her sonucu kontrol eder ve bir işin ne zaman bittiğine karar
verir. Sekiz alt ajan şunlardır:

| Ajan | Sorumluluk |
| --- | --- |
| `pixel-artist` | sanat yönetimi, varlık tanımları, üretilen sprite ve karolar |
| `npc-story-engineer` | karakterler, dallanan diyaloglar, bayraklar, görevler |
| `world-builder-level-design` | harita düzeni, çarpışma, başlangıç noktaları, çıkışlar |
| `world-builder-environmental-content` | dekor, ilgi çekici noktalar, bölge atmosferi |
| `ui-engineer` | menüler, HUD, diyalog kutusu, envanter ve kayıt ekranları |
| `gameplay-engineer` | hareket, oyun durumu, envanter, görevler, kaydetme |
| `qa-tester` | testler, test çalıştırmaları, hata raporları |
| `bug-fixer` | regresyon testleriyle kök neden düzeltmeleri |

Ayrıntılar: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Mimari

Director bir alt ajan değil, becerinin kendisidir; çünkü isteklerinizi görmesi ve tek bir doğruluk
kaynağını (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` ve beş kısa belge daha) yönetmesi gerekir.
Uzmanlar görev tanımı alır, sorumlu oldukları dosyalar üzerinde çalışır ve rapor verir; başka ajan
başlatamazlar. Oyun içeriği motordan bağımsız bir `data/` klasöründe durur; böylece hikâye, seviye ve
çevre çalışmaları paralel yürüyebilir ve motor başlatılmadan denetlenebilir. Alt ajanlar
kullanılamıyorsa Director aynı adımları sırayla kendisi uygular. Bkz. [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Ön koşullar

- Claude Code (2.1.312 sürümüyle kontrol edildi).
- Python 3.9 veya daha yenisi; ek paket gerekmez.
- Gerçek oyunlar için seçtiğiniz motor, örneğin Godot 4 ya da MonoGame için .NET SDK. Beceri, neyin
  kurulu olduğunu kontrol eder ve bir şey kurmadan önce size sorar.

<!-- section: installation -->
## Kurulum

Depoyu klonlayın, ardından kurulum şeklini seçin. Her değişikliği önce `--dry-run` ile önizleyin:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

Proje kapsamı `<project>/.claude/` dizinine, kullanıcı kapsamı `~/.claude/` dizinine yazar. Kurulum
aracının oluşturmadığı mevcut dosyalar asla değiştirilmez. Bir kurulumu yenilemek için `--update`
kullanın (eski dosyalar yedeklenir); yalnızca aracın kurduğu ve değişmemiş dosyaları kaldırmak için
`--uninstall` kullanın. Claude Code'u doğrudan bu depo içinde de çalıştırabilir ya da klasörleri elle
kopyalayabilirsiniz. Tüm seçenekler [INSTALLATION.md](../INSTALLATION.md) dosyasındadır.

<!-- section: quick-start -->
## Hızlı başlangıç

Proje klasörünüzde Claude Code'u açın ve şunu yazın:

```text
/pixel-art-game-studio Küçük bir kasaba, bir orman, üç NPC, dallanan diyaloglar, gece-gündüz döngüsü ve kayıt sistemi olan özgün, huzurlu, yukarıdan bakışlı bir piksel sanatı oyunu oluştur.
```

Director makul varsayılanlar seçer, kısa bir tasarım yazar ve önce küçük, oynanabilir bir sürüm
kurar. Tek bir uzmanı doğrudan çağırmak için adını anın, örneğin `@agent-qa-tester`.

<!-- section: examples -->
## Örnek istekler

```text
/pixel-art-game-studio İki NPC ve iki sonu olan bir görev içeren sisli bir bataklık bölgesi ekle.
/pixel-art-game-studio Kasaba boş görünüyor. Ayrıntı ve küçük keşifler ekle ama yolları açık tut.
/pixel-art-game-studio Bu oyunu incele, mevcut tüm testleri çalıştır ve yeniden üretilebilen hataları düzelt.
```

İsteklerinizi istediğiniz dilde yazabilirsiniz. Eksiksiz bir örnek [examples](../../examples/example-game-idea.md)
klasöründedir.

<!-- section: workflows -->
## İş akışları

- **Oyun oluşturma**: oynanabilir en küçük döngüyle başlayarak fikirden teslimata 14 aşama.
- **Oyunu genişletme**: mevcut projeyi incelemek, en küçük tutarlı değişikliği yapmak, regresyonları
  kontrol etmek.
- **Test ve düzeltme**: gerçek testleri çalıştırmak, hataları raporlamak, doğrulananları sınırlı sayıda
  denemeyle düzeltmek.
- **Varlık üretimi**: önce sanat yönetimi, ardından tanımlar, PNG dosyaları ve önizlemeler.
- **Sürüm kontrolü**: kanıta dayalı bir karar: hazır, bilinen sorunlarla hazır veya hazır değil.

Genel bakış: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Test ve hata düzeltme

QA test uzmanı, oyunun gerçekte hangi araçlara sahip olduğunu tespit eder, kabul kriterlerini teste
dönüştürür, bunları çalıştırır ve önem derecesi, adımlar ve kanıt içeren hata raporları yazar. Hata
düzeltici her hatayı yeniden üretir, kök nedeni düzeltir, bir regresyon testi ekler ve kontrolleri
tekrar çalıştırır. Testleri zayıflatmak veya silmek asla serbest değildir. Bu deponun kendisini test
etmek için:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Ayrıntılar: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Sınırlamalar

- Kendi başına bitmiş ticari oyunlar üretmez; geri bildirimlerinizle büyüyen, çalışan bir temel
  bekleyin.
- Kurulu bir motor olmadan yalnızca veriler, varlıklar ve motordan bağımsız mantık doğrulanabilir.
- Yapısal kontroller grafiklerin güzel görünüp görünmediğini ya da oyunun eğlenceli olup olmadığını
  değerlendiremez; bunun için bir insan gerekir.
- Çeviriler makine desteklidir ve anadili konuşanların incelemesini beklemektedir.

<!-- section: troubleshooting -->
## Sorun giderme

Beceri görünmüyorsa `SKILL.md` dosyasının `.claude/skills/pixel-art-game-studio/` içinde olduğunu
kontrol edin. Ajanlar bulunamıyorsa `.claude/agents/` oluşturulduktan sonra Claude Code'u yeniden
başlatın. Kurulum aracı 2 koduyla çıkıyorsa kendisinin oluşturmadığı bir dosya bulmuştur; yazdırdığı
planı okuyun. Daha fazla yanıt için [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Katkıda bulunma

Katkılar memnuniyetle karşılanır, özellikle bu çevirilerin anadili konuşanlarca incelenmesi. Bir pull
request açmadan önce [CONTRIBUTING.md](../CONTRIBUTING.md) ve [Davranış Kuralları](../CODE_OF_CONDUCT.md)
belgelerini okuyun.

<!-- section: license -->
## Lisans

Pixel Art Game Studio, [MIT Lisansı](../../LICENSE) ile yayımlanmıştır. Onunla yaptığınız oyunlar size
aittir.
