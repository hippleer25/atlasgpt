import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Dimensions,
  Animated,
  Image,
  Linking,
} from 'react-native';
import { useFonts } from 'expo-font';
import usFlag from './assets/uk-flag.png';
import brFlag from './assets/br-flag.png';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTitleVisible, setIsTitleVisible] = useState(true);
  const [isButtonsVisible, setIsButtonsVisible] = useState(true);
  const [textInputHeight, setTextInputHeight] = useState(40);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [termsMessageVisible, setTermsMessageVisible] = useState(true);
  const [language, setLanguage] = useState('pt');
  const [currentScreen, setCurrentScreen] = useState('main');
  const scrollViewRef = useRef();
  const maxTextInputHeight = Dimensions.get('window').height * 0.3;
  const buttonColorAnim = useRef(new Animated.Value(0)).current;

  const [fontsLoaded] = useFonts({
    'Yantramanav-Bold': require('./assets/fonts/Yantramanav-Bold.ttf'),
    Inter: require('./assets/fonts/Inter-Regular.ttf'),
    'Inter-Italic': require('./assets/fonts/Inter-Italic.ttf'),
    'Inter-Bold': require('./assets/fonts/Inter-Bold.ttf'),
  });

  const translations = {
    en: {
      goToAtlas: 'GO TO ATLAS',
      languageToggle: 'pt',
      title: 'AtlasGPT',
      titleDescription:
        'With AtlasGPT, you will receive accurate recommendations for starting businesses, enhanced with artificial intelligence. Tell us a little more about yourself and the projects you would like to start. AtlasGPT will guide you through the world of business!',
      button1: 'I already have a location',
      button2: 'I already have a sector',
      button3: 'I have a sector and a location',
      termsText:
        'By starting the conversation, you agree to the ',
      privacyPolicy: 'Privacy Policy',
      termsOfService: 'Terms of Service',
      placeholderText: 'Type a message...',
      sendButtonText: 'Send',
      loadingText: 'Loading...',
      errorMessage: 'Error: ',
      privacyPolicyTitle: 'Privacy Policy',
      termsOfServiceTitle: 'Terms of Service',
      backButtonText: 'Back',
    },
    pt: {
      goToAtlas: 'IR PARA O ATLAS',
      languageToggle: 'en',
      title: 'AtlasGPT',
      titleDescription:
        'Com o AtlasGPT, você receberá recomendações precisas para abertura de negócios, aprimorado com inteligência artificial. Conte um pouco mais sobre você e sobre os projetos que gostaria de iniciar. O AtlasGPT o guiará pelo mundo dos negócios!',
      button1: 'Eu já tenho uma localização',
      button2: 'Eu já tenho um setor econômico',
      button3: 'Eu tenho um setor e uma localização',
      termsText:
        'Ao iniciar a conversa, você concorda com a ',
      privacyPolicy: 'Política de Privacidade',
      termsOfService: 'Termos de Serviço',
      placeholderText: 'Digite uma mensagem...',
      sendButtonText: 'Enviar',
      loadingText: 'Carregando...',
      errorMessage: 'Erro: ',
      privacyPolicyTitle: 'Política de Privacidade',
      termsOfServiceTitle: 'Termos de Serviço',
      backButtonText: 'Voltar',
    },
  };

  const currentTranslations = translations[language];

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const tokenResponse = await fetch('http://localhost:5000/api/token');
        const tokenData = await tokenResponse.json();
        setToken(tokenData.user_token);
      } catch (error) {
        console.error('Failed to fetch token:', error);
      }
    };
    fetchToken();
  }, []);

  useEffect(() => {
    Animated.timing(buttonColorAnim, {
      toValue: isLoading ? 1 : 0,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [isLoading]);

  const sendMessage = async (text) => {
    const trimmedText = text.trim();
    if (trimmedText === '' || isLoading) return;
    const userMessage = { type: 'user', text: trimmedText };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputText('');
    setTextInputHeight(40);
    setIsTitleVisible(false);
    setIsLoading(true);
    setTermsMessageVisible(false);
    setIsButtonsVisible(false);

    if (!token) {
      console.error('No token available');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/api?q=${encodeURIComponent(
          trimmedText
        )}&t=${encodeURIComponent(token)}&lang=${encodeURIComponent(language)}`,
        {
          method: 'GET',
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let textChunk = '';

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value, { stream: !done });
        textChunk += chunk;

        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          if (updatedMessages[updatedMessages.length - 1].type === 'bot') {
            updatedMessages[updatedMessages.length - 1] = {
              ...updatedMessages[updatedMessages.length - 1],
              text: textChunk,
            };
          } else {
            updatedMessages.push({ type: 'bot', text: textChunk });
          }
          return updatedMessages;
        });

        await new Promise((resolve) => setTimeout(resolve, 1));
      }

      setIsLoading(false);
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: 'bot', text: `${currentTranslations.errorMessage}${error.message}` },
      ]);
      setIsLoading(false);
    }
  };

  const handleButtonPress = (text) => {
    setInputText(text);
    sendMessage(text);
  };

  const handleContentSizeChange = (event) => {
    const newHeight = event.nativeEvent.contentSize.height;
    setTextInputHeight(Math.min(Math.max(40, newHeight), maxTextInputHeight));
  };

  const formatText = (text, isBot) => {
    const lines = text.split('\n');

    return lines.map((line, index) => {
      let headingLevel = 0;
      let content = line;

      if (line.startsWith('### ')) {
        headingLevel = 3;
        content = line.replace(/^###\s+/, '');
      } else if (line.startsWith('## ')) {
        headingLevel = 2;
        content = line.replace(/^##\s+/, '');
      } else if (line.startsWith('# ')) {
        headingLevel = 1;
        content = line.replace(/^#\s+/, '');
      }

      const regex = /(\*\*[^*]+\*\*|\*[^\*]+\*|_[^_]+_)/g;
      const parts = content.split(regex).filter((part) => part !== '');

      const formattedParts = parts.map((part, idx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <Text key={idx} style={styles.bold}>
              {part.slice(2, -2)}
            </Text>
          );
        } else if (
          (part.startsWith('_') && part.endsWith('_')) ||
          (part.startsWith('*') && part.endsWith('*'))
        ) {
          return (
            <Text key={idx} style={styles.italic}>
              {part.slice(1, -1)}
            </Text>
          );
        } else {
          return part;
        }
      });

      let textStyle = [styles.messageText];

      if (isBot) {
        textStyle.push(styles.botMessageText);
      }

      if (headingLevel === 1) {
        textStyle.push(styles.heading1);
      } else if (headingLevel === 2) {
        textStyle.push(styles.heading2);
      } else if (headingLevel === 3) {
        textStyle.push(styles.heading3);
      }

      return (
        <Text key={index} style={textStyle}>
          {formattedParts}
          {'\n'}
        </Text>
      );
    });
  };

  const buttonBackgroundColor = buttonColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['#032640', '#94a3b8'],
  });

  const handleKeyPress = (e) => {
    if (Platform.OS === 'web' && e.nativeEvent.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      sendMessage(inputText);
    }
  };

  const toggleLanguage = () => {
    setLanguage((prevLang) => (prevLang === 'en' ? 'pt' : 'en'));
  };

  if (!fontsLoaded) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>{currentTranslations.loadingText}</Text>
      </View>
    );
  }

  const { width } = Dimensions.get('window');
  const isDesktop = width >= 1024;
  const isHeaderVisible = isDesktop || !isTitleVisible;
  const contentMarginTop = isHeaderVisible
    ? Platform.OS === 'android' || Platform.OS === 'ios'
      ? 50
      : 70
    : 0;

  const lastMessage = messages[messages.length - 1];
  const botHasStartedTyping =
    lastMessage && lastMessage.type === 'bot' && lastMessage.text && lastMessage.text.length > 0;

  const showLoadingIndicator = isLoading && !botHasStartedTyping;

  const renderPrivacyPolicy = () => {
    const privacyPolicyText =
      language === 'en'
        ? `
## Privacy Policy
This privacy policy applies to the Atlas de Oportunidades app (and its associated LLM service AtlasGPT) which are projects of the Grupo de Pesquisa em Marketing e Consumo (GPMC) at the Universidade Federal do Rio Grande do Sul (UFRGS).

### Information Collection and Use
When you use the Atlas de Oportunidades app, we may collect information such as: (i) your device's IP address, (ii) the pages you visit within the app and the time spent on them, (iii) your device's operating system, (iv) your email address, (v) your password, (vi) your gender, (vii) your year of birth, (viii) your nationality (national or foreign), (ix) your state of birth, (x) your city of birth, (xi) your zip code, (xii) the state you selected, (xiii) the city you selected, (xiv) your education level, (xv) your area of study, (xvi) your professional experience, (xvii) your years of experience, (xviii) your goals, (xix) your target audience, (xx) your economic sector, (xxi) your experience in starting a business, (xxii) your investment capacity, (xxiii) your risk tolerance, (xxiv) your self-confidence, (xxv) your competitors, (xxvi) your geographic level, (xxvii) relevant public policies, (xxviii) the type of business, (xxix) estimated costs, and (xxx) business size. We do not share this information with any third parties. We only use this information internally to improve the app's performance and functionality, and to enhance the services we provide to our users.

The app also collects your device's location, which allows us to provide location-based features and personalized content. This location data is used solely for the purpose of improving our services, and is never shared with any external parties.

### Data Retention and Security
We are committed to protecting the confidentiality of your information. We employ physical, electronic, and procedural safeguards to ensure the security of the data we process and maintain.

We will retain user data for as long as necessary to provide our services and improve our research. If you would like us to delete any of your personal data, please contact us at gpmc.ufrgs@gmail.com and we will respond promptly.

### Use of Data for Research
The data collected through the Atlas de Oportunidades app and AtlasGPT is used solely for the purpose of improving our scientific research and enhancing the services we provide to our users. We do not share this data with any third parties. Our goal is to use the insights gained from this data to better understand user needs and preferences, and to develop more effective solutions to benefit our community.

### Changes to this Policy
This privacy policy may be updated from time to time. We will notify you of any changes by updating the policy on this page. Your continued use of the app after any such updates constitutes your acceptance of the revised policy.

### Contact Us
If you have any questions or concerns about our privacy practices, please don't hesitate to contact us at gpmc.ufrgs@gmail.com.
        `
        : `
## Política de Privacidade
Esta política de privacidade se aplica ao aplicativo Atlas de Oportunidades (e seu serviço de LLM associado AtlasGPT), que são projetos do Grupo de Pesquisa em Marketing e Consumo (GPMC) da Universidade Federal do Rio Grande do Sul (UFRGS).

### Coleta e Uso de Informações
Quando você usa o aplicativo Atlas de Oportunidades, podemos coletar informações como: (i) o endereço IP do seu dispositivo, (ii) as páginas que você visita dentro do aplicativo e o tempo gasto nelas, (iii) o sistema operacional do seu dispositivo, (iv) seu endereço de e-mail, (v) sua senha, (vi) seu gênero, (vii) seu ano de nascimento, (viii) sua nacionalidade (nacional ou estrangeira), (ix) seu estado de nascimento, (x) sua cidade de nascimento, (xi) seu CEP, (xii) o estado que você selecionou, (xiii) a cidade que você selecionou, (xiv) seu nível de escolaridade, (xv) sua área de estudo, (xvi) sua experiência profissional, (xvii) seus anos de experiência, (xviii) seus objetivos, (xix) seu público-alvo, (xx) seu setor econômico, (xxi) sua experiência em iniciar um negócio, (xxii) sua capacidade de investimento, (xxiii) sua tolerância ao risco, (xxiv) sua autoconfiança, (xxv) seus concorrentes, (xxvi) seu nível geográfico, (xxvii) as políticas públicas relevantes, (xxviii) o tipo de negócio, (xxix) custos estimados e (xxx) tamanho do negócio. Não compartilhamos essas informações com terceiros. Usamos essas informações apenas internamente para melhorar o desempenho e a funcionalidade do aplicativo e para aprimorar os serviços que fornecemos aos nossos usuários.

O aplicativo também coleta a localização do seu dispositivo, o que nos permite fornecer recursos baseados em localização e conteúdo personalizado. Esses dados de localização são usados exclusivamente para melhorar nossos serviços e nunca são compartilhados com partes externas.

### Retenção e Segurança de Dados
Nos comprometemos a proteger a confidencialidade de suas informações. Empregamos salvaguardas físicas, eletrônicas e processuais para garantir a segurança dos dados que processamos e mantemos.

Reteremos os dados do usuário pelo tempo necessário para fornecer nossos serviços e melhorar nossa pesquisa. Se você quiser que deletemos algum de seus dados pessoais, entre em contato conosco pelo e-mail gpmc.ufrgs@gmail.com e responderemos prontamente.

### Uso de Dados para Pesquisa
Os dados coletados através do aplicativo Atlas de Oportunidades e AtlasGPT são usados exclusivamente para melhorar nossa pesquisa científica e aprimorar os serviços que fornecemos aos nossos usuários. Não compartilhamos esses dados com terceiros. Nosso objetivo é usar os insights obtidos com esses dados para entender melhor as necessidades e preferências dos usuários e desenvolver soluções mais eficazes para beneficiar nossa comunidade.

### Alterações nesta Política
Esta política de privacidade pode ser atualizada periodicamente. Notificaremos você de quaisquer alterações atualizando a política nesta página. Seu uso contínuo do aplicativo após qualquer uma dessas atualizações constitui a sua aceitação da política revisada.

### Entre em Contato Conosco
Se você tiver alguma dúvida ou preocupação sobre nossas práticas de privacidade, não hesite em entrar em contato conosco pelo e-mail gpmc.ufrgs@gmail.com.2
        `;

    return (
      <ScrollView style={[styles.privacyPolicyContainer, { marginTop: contentMarginTop }]}>
        <View style={styles.privacyPolicyContent}>
          {formatText(privacyPolicyText, true)}
          <TouchableOpacity style={styles.backButton} onPress={() => setCurrentScreen('main')}>
            <Text style={styles.backButtonText}>{currentTranslations.backButtonText}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  };

  const renderTermsOfService = () => {
    const termsOfServiceText =
      language === 'en'
        ? `
## Terms of Service
These terms and conditions apply to the Atlas de Oportunidades website (and its associated LLM service AtlasGPT) which are projects of the Grupo de Pesquisa em Marketing e Consumo (GPMC) at the Universidade Federal do Rio Grande do Sul (UFRGS).
By accessing or using the Atlas de Oportunidades website, you automatically agree to the following terms. It is strongly advised that you thoroughly read and understand these terms prior to using the website.

### Intellectual Property
All trademarks, copyrights, database rights, and other intellectual property rights related to the Atlas de Oportunidades website and its content remain the property of the Service Provider. Unauthorized copying, modification, translation, or creation of derivative versions of the website or our trademarks is strictly prohibited.

### Website Updates and Availability
The Service Provider reserves the right to modify the Atlas de Oportunidades website or charge for its services at any time. Any changes to pricing or paid services will be clearly communicated.

The Service Provider does not guarantee that the website will always be updated or compatible with all browser versions and devices. However, you agree to always use the latest version of the website when accessing it.

### Third-Party Services
The Atlas de Oportunidades website may utilize third-party services such as web hosting, analytics, and content delivery networks. You are responsible for complying with the terms and conditions of these third-party providers.

### Limitations of Liability
The Service Provider cannot be held responsible if the website does not function due to lack of internet access, browser compatibility issues, or problems with your device. You are responsible for any charges incurred from your internet service provider while using the website.

The Service Provider strives to ensure the accuracy of the information provided through the website, but cannot be liable for any loss or damages resulting from reliance on this information.

### Changes to Terms of Service
The Service Provider may update these Terms of Service periodically. It is your responsibility to regularly review this page for any changes. Continued use of the website after any updates constitutes acceptance of the revised terms.

### Contact Us
If you have any questions or suggestions about the Terms of Service, please contact the Service Provider at gpmc.ufrgs@gmail.com.
        `
        : `
## Termos de Serviço
Esses termos e condições aplicam-se ao site Atlas de Oportunidades (e ao seu serviço associado de LLM, AtlasGPT), que são projetos do Grupo de Pesquisa em Marketing e Consumo (GPMC) da Universidade Federal do Rio Grande do Sul (UFRGS). Ao acessar ou usar o site Atlas de Oportunidades, você concorda automaticamente com os seguintes termos. É fortemente recomendado que você leia e compreenda estes termos antes de utilizar o site.

### Propriedade Intelectual
Todas as marcas, direitos autorais, direitos de banco de dados e outros direitos de propriedade intelectual relacionados ao site Atlas de Oportunidades e seu conteúdo permanecem de propriedade do Provedor do Serviço. A cópia, modificação, tradução ou criação de versões derivadas do site ou de nossas marcas é estritamente proibida.

### Atualizações e Disponibilidade do Site
O Provedor do Serviço reserva-se o direito de modificar o site Atlas de Oportunidades ou cobrar por seus serviços a qualquer momento. Quaisquer mudanças nos preços ou na funcionalidade do site serão notificadas com antecedência, e o uso continuado do site após tais mudanças implicará aceitação dos novos termos.

### Limitação de Responsabilidade
O Provedor do Serviço não se responsabiliza por qualquer perda ou dano, direto ou indireto, decorrente do uso do site Atlas de Oportunidades. Todo o conteúdo do site é fornecido "como está" e "conforme disponível", sem qualquer garantia, expressa ou implícita.

### Links para Outros Sites
O site Atlas de Oportunidades pode conter links para sites de terceiros. Esses links são fornecidos apenas para sua conveniência, e o Provedor do Serviço não se responsabiliza pelo conteúdo, precisão ou práticas de privacidade desses sites.

### Lei Aplicável
Esses termos são regidos pelas leis da República Federativa do Brasil. Qualquer disputa decorrente ou relacionada a estes termos será resolvida exclusivamente nos tribunais brasileiros competentes.

### Modificações aos Termos de Serviço
O Provedor do Serviço reserva-se o direito de revisar e modificar estes Termos de Serviço a qualquer momento, sem aviso prévio. A versão mais atual estará sempre disponível no site. O uso contínuo do site após quaisquer alterações nos Termos de Serviço constitui sua aceitação dessas alterações.

### Contato
Para qualquer dúvida ou sugestão relacionada a estes Termos de Serviço, entre em contato com o Grupo de Pesquisa em Marketing e Consumo da UFRGS por meio do e-mail gpmc@ufrgs.br.
        `;

    return (
      <ScrollView style={[styles.privacyPolicyContainer, { marginTop: contentMarginTop }]}>
        <View style={styles.privacyPolicyContent}>
          {formatText(termsOfServiceText, true)}
          <TouchableOpacity style={styles.backButton} onPress={() => setCurrentScreen('main')}>
            <Text style={styles.backButtonText}>{currentTranslations.backButtonText}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  };

  if (currentScreen === 'privacyPolicy') {
    return (
      <View style={styles.container}>
        {isHeaderVisible && (
          <View style={styles.header}>
            <View style={styles.headerRight}>
              <TouchableOpacity style={styles.languageButton} onPress={toggleLanguage}>
                <Image
                  source={language === 'en' ? brFlag : usFlag}
                  style={styles.languageButtonImage}
                  resizeMode="contain"
                />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.topButton}
                onPress={() => Linking.openURL('http://atlas-oportunidades.nuvem.ufrgs.br/')}
              >
                <Text style={styles.topButtonText}>{currentTranslations.goToAtlas}</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        {renderPrivacyPolicy()}
      </View>
    );
  }

  if (currentScreen === 'termsOfService') {
    return (
      <View style={styles.container}>
        {isHeaderVisible && (
          <View style={styles.header}>
            <View style={styles.headerRight}>
              <TouchableOpacity style={styles.languageButton} onPress={toggleLanguage}>
                <Image
                  source={language === 'en' ? brFlag : usFlag}
                  style={styles.languageButtonImage}
                  resizeMode="contain"
                />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.topButton}
                onPress={() => Linking.openURL('http://atlas-oportunidades.nuvem.ufrgs.br/')}
              >
                <Text style={styles.topButtonText}>{currentTranslations.goToAtlas}</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        {renderTermsOfService()}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {isHeaderVisible && (
        <View style={styles.header}>
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.languageButton} onPress={toggleLanguage}>
              <Image
                source={language === 'en' ? brFlag : usFlag}
                style={styles.languageButtonImage}
                resizeMode="contain"
              />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.topButton}
              onPress={() => Linking.openURL('http://atlas-oportunidades.nuvem.ufrgs.br/')}
            >
              <Text style={styles.topButtonText}>{currentTranslations.goToAtlas}</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      <KeyboardAvoidingView
        style={[
          styles.contentContainer,
          isDesktop && styles.desktopContainer,
          { marginTop: contentMarginTop },
        ]}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.select({ ios: 0, android: 80 })}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContainer}
          ref={scrollViewRef}
          onContentSizeChange={() => scrollViewRef.current.scrollToEnd({ animated: true })}
          showsVerticalScrollIndicator={false}
        >
          {isTitleVisible && (
            <View style={styles.titleContainer}>
              <Text style={styles.title}>{currentTranslations.title}</Text>
              <Text style={styles.titleDescription}>{currentTranslations.titleDescription}</Text>
            </View>
          )}

          {messages.map((msg, index) => (
            <View
              key={index}
              style={[
                styles.messageContainer,
                msg.type === 'user' ? styles.userMessage : styles.botMessage,
              ]}
            >
              <Text style={[styles.messageText, msg.type === 'bot' && styles.botMessageText]}>
                {formatText(msg.text, msg.type === 'bot')}
              </Text>
            </View>
          ))}

          {showLoadingIndicator && (
            <View style={[styles.messageContainer, styles.botMessage]}>
              <Text style={[styles.messageText, styles.botMessageText]}>...</Text>
            </View>
          )}
        </ScrollView>

        {isButtonsVisible && (
          <View style={styles.buttonContainer}>
            <View style={styles.infoButtonsGrid}>
              <TouchableOpacity
                style={styles.infoButton}
                onPress={() => handleButtonPress(currentTranslations.button1)}
              >
                <Text style={styles.infoButtonText}>{currentTranslations.button1}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.infoButton}
                onPress={() => handleButtonPress(currentTranslations.button2)}
              >
                <Text style={styles.infoButtonText}>{currentTranslations.button2}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.infoButton}
                onPress={() => handleButtonPress(currentTranslations.button3)}
              >
                <Text style={styles.infoButtonText}>{currentTranslations.button3}</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {termsMessageVisible && (
          <View style={styles.termsMessage}>
            <Text style={styles.termsText}>
              {currentTranslations.termsText}
              <Text style={styles.termsLink} onPress={() => setCurrentScreen('privacyPolicy')}>
                {currentTranslations.privacyPolicy}
              </Text>{' '}
              {language === 'en' ? 'and the ' : 'e os '}
              <Text style={styles.termsLink} onPress={() => setCurrentScreen('termsOfService')}>
                {currentTranslations.termsOfService}
              </Text>
              {language === 'en'
                ? ' of the Atlas of Opportunities.'
                : ' do Atlas de Oportunidades.'}
            </Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={[styles.textInput, { height: textInputHeight }]}
            multiline
            value={inputText}
            onChangeText={setInputText}
            onContentSizeChange={handleContentSizeChange}
            placeholder={currentTranslations.placeholderText}
            placeholderTextColor="#94a3b8"
            onKeyPress={handleKeyPress}
            scrollEnabled={true}
          />
          <Animated.View style={[styles.sendButton, { backgroundColor: buttonBackgroundColor }]}>
            <TouchableOpacity onPress={() => sendMessage(inputText)} disabled={isLoading}>
              <Text style={styles.sendButtonText}>{currentTranslations.sendButtonText}</Text>
            </TouchableOpacity>
          </Animated.View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#64748b',
    fontFamily: 'Inter',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: '#ffffff',
    padding: Platform.OS === 'android' || Platform.OS === 'ios' ? 6 : 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
    zIndex: 1000,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  languageButton: {
    backgroundColor: '#032640',
    paddingVertical: Platform.OS === 'android' || Platform.OS === 'ios' ? 2 : 4,
    paddingHorizontal: Platform.OS === 'android' || Platform.OS === 'ios' ? 8 : 12,
    borderRadius: 6,
    marginRight: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  languageButtonImage: {
    width: 20,
    height: 20,
  },
  topButton: {
    backgroundColor: '#032640',
    paddingVertical: Platform.OS === 'android' || Platform.OS === 'ios' ? 6 : 12,
    paddingHorizontal: Platform.OS === 'android' || Platform.OS === 'ios' ? 16 : 24,
    borderRadius: 8,
    marginRight: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  topButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    fontFamily: 'Inter',
  },
  contentContainer: {
    flex: 1,
  },
  desktopContainer: {
    alignSelf: 'center',
    width: '100%',
    maxWidth: 800,
    padding: 20,
    height: '100%',
  },
  scrollView: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollContainer: {
    padding: 16,
    flexGrow: 1,
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: Platform.OS === 'android' || Platform.OS === 'ios' ? 16 : 32,
    marginTop: Platform.OS === 'android' || Platform.OS === 'ios' ? 16 : 32,
  },
  title: {
    fontSize: Platform.OS === 'android' || Platform.OS === 'ios' ? 48 : 96,
    fontFamily: 'Yantramanav-Bold',
    color: '#032640',
    marginBottom: Platform.OS === 'android' || Platform.OS === 'ios' ? 8 : 16,
    textAlign: 'center',
  },
  titleDescription: {
    fontSize: Platform.OS === 'android' || Platform.OS === 'ios' ? 14 : 20,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: Platform.OS === 'android' || Platform.OS === 'ios' ? 20 : 28,
    paddingHorizontal: 16,
    fontFamily: 'Inter',
  },
  termsMessage: {
    paddingHorizontal: 16,
    paddingVertical: 4,
    alignItems: 'center',
  },
  termsText: {
    color: '#1e293b',
    fontSize: 12,
    fontFamily: 'Inter',
    textAlign: 'center',
  },
  termsLink: {
    color: '#032640',
    fontWeight: 'bold',
  },
  buttonContainer: {
    padding: 16,
  },
  infoButtonsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  infoButton: {
    backgroundColor: '#ffffff',
    padding: Platform.OS === 'android' || Platform.OS === 'ios' ? 12 : 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    flex: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  infoButtonText: {
    color: '#032640',
    fontSize: Platform.OS === 'android' || Platform.OS === 'ios' ? 14 : 16,
    textAlign: 'center',
    fontFamily: 'Inter',
  },
  inputContainer: {
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    padding: Platform.OS === 'android' || Platform.OS === 'ios' ? 12 : 16,
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#ffffff',
    gap: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    margin: 16,
  },
  textInput: {
    flex: 1,
    padding: 12,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    fontSize: 16,
    fontFamily: 'Inter',
    color: '#1e293b',
    minHeight: 48,
    maxHeight: Dimensions.get('window').height * 0.3,
    overflow: 'hidden',
  },
  sendButton: {
    paddingVertical: Platform.OS === 'android' || Platform.OS === 'ios' ? 10 : 12,
    paddingHorizontal: Platform.OS === 'android' || Platform.OS === 'ios' ? 16 : 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#032640',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: Platform.OS === 'android' || Platform.OS === 'ios' ? 14 : 16,
    fontWeight: '600',
    fontFamily: 'Inter',
    textAlignVertical: 'center',
  },
  messageContainer: {
    maxWidth: '85%',
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#032640',
    borderTopRightRadius: 4,
  },
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 24,
    fontFamily: 'Inter',
    color: '#ffffff',
  },
  botMessageText: {
    color: '#1e293b',
  },
  bold: {
    fontFamily: 'Inter-Bold',
  },
  italic: {
    fontFamily: 'Inter-Italic',
  },
  heading1: {
    fontSize: 24,
    fontFamily: 'Inter-Bold',
    marginBottom: 8,
    color: '#032640',
    textAlign: 'center',
  },
  heading2: {
    fontSize: 20,
    fontFamily: 'Inter-Bold',
    marginBottom: 6,
    color: '#032640',
  },
  heading3: {
    fontSize: 18,
    fontFamily: 'Inter-Bold',
    marginBottom: 4,
    color: '#032640',
  },
  privacyPolicyContainer: {
    flex: 1,
    padding: 16,
  },
  privacyPolicyContent: {
    maxWidth: 800,
    alignSelf: 'center',
  },
  backButton: {
    marginTop: 24,
    alignSelf: 'center',
    backgroundColor: '#032640',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontFamily: 'Inter-Bold',
  },
});
export default App;
